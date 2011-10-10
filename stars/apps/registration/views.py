from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.forms import widgets
from django.conf import settings

from datetime import datetime, date, timedelta
import urllib2, re, sys
from xml.etree.ElementTree import fromstring

from stars.apps.institutions.models import Institution
from stars.apps.registration.forms import *
from stars.apps.registration.utils import is_canadian_zipcode, is_usa_zipcode
from stars.apps.accounts.utils import respond, connect_iss
from stars.apps.helpers import watchdog, flashMessage
from stars.apps.tool.admin.watchdog.models import ERROR
from stars.apps.tool.my_submission.views import _get_active_submission
from stars.apps.accounts import xml_rpc
from stars.apps.submissions.models import *
from stars.apps.credits.models import CreditSet
from stars.apps.helpers.forms.views import FormActionView
from stars.apps.accounts.mixins import AuthenticatedMixin
from stars.apps.submissions.utils import init_credit_submissions
from stars.apps.accounts import utils as auth_utils
from stars.apps.notifications.models import EmailTemplate

from zc.authorizedotnet.processing import CcProcessor
from zc.creditcard import (AMEX, DISCOVER, MASTERCARD, VISA, UNKNOWN_CARD_TYPE)
from aashe.issdjango.models import Organizations

def reg_international(request):
    """
        First step for registering an international institution
    """
    response = _confirm_login(request)
    if response: return response
    
    form = WriteInInstitutionForm()
    if request.method == 'POST':
        form = WriteInInstitutionForm(request.POST)
        if form.is_valid():
            
            institution = Institution(name=form.cleaned_data['institution_name'], international=True)
            institution.slug = slugify(institution.name)
            # If they've already got this institution in their session don't overwrite it
            # it might have contact info
            selected_institution = request.session.get('selected_institution')
            if not selected_institution or selected_institution.name != institution.name:
                selected_institution = institution
            request.session['selected_institution'] = selected_institution
            return HttpResponseRedirect('/register/step2/')

    template = "registration/international.html"
    context = {'form': form,}
    return respond(request, template, context)

def reg_select_institution(request):
    """
        STEP 1: User selects an institution from the pull-down menu
         - store the selected institution in the Session (not the DB), and move on to the next step
    """
    response = _confirm_login(request)
    if response: return response
    
    # Get the list of schools as choices
    institution_list = []
    institution_list_lookup = {}
    org_types = ('I',
                 'Four Year Institution',
                 'Two Year Institution',
                 'Graduate Institution',
                 'System Office')
    countries = ('Canada', 'United States of America')             
    
    for inst in Organizations.objects.filter(org_type__in=org_types,
                                             country__in=countries).order_by('org_name'):
        if inst.city and inst.state:
            institution_list.append((inst.account_num, "%s, %s, %s" % (inst.org_name, inst.city, inst.state)))
        else:
            institution_list.append((inst.account_num, inst.org_name))
        institution_list_lookup[inst.account_num] = inst.org_name
    
    # Generate the school choice form
    form = RegistrationSchoolChoiceForm()
    if request.method == 'POST':
        form = RegistrationSchoolChoiceForm(request.POST)
        if form.is_valid():
            aashe_id = form.cleaned_data['aashe_id']
            # print >> sys.stderr, institution_list_lookup
            name = institution_list_lookup[aashe_id]
            
            # Redirect to "Purchase additional SS view
            # if the institution already has an account
            try:
                institution = Institution.objects.get(aashe_id=aashe_id)
                if institution != request.user.current_inst or request.user.is_staff:
                    auth_utils.change_institution(request, institution)
                return HttpResponseRedirect('/tool/manage/submissionsets/purchase/')
            except Institution.DoesNotExist:
                institution = Institution(aashe_id=aashe_id, name=name)
                # If they've already got this institution in their session don't overwrite it
                # it might have contact info
                selected_institution = request.session.get('selected_institution')
                if not selected_institution or selected_institution.aashe_id != institution.aashe_id:
                    selected_institution = institution
                
                selected_institution.update_from_iss()
                selected_institution.set_slug_from_iss_institution(form.cleaned_data['aashe_id'])
                request.session['selected_institution'] = selected_institution
                return HttpResponseRedirect('/register/step2/')
        else:
            e = form.errors
            # Since this is a pull-down menu, there is really no way for this to happen.
            watchdog.log("Registration", "The institution select form didn't validate.", watchdog.ERROR)
            
    form.fields['aashe_id'].widget = widgets.Select(choices=institution_list)
    
    template = "registration/select_institution.html"
    context = {'form': form,}
    return respond(request, template, context)
    
def reg_contact_info(request):
    """
        STEP 2: Displays the contact forms for an institution's registration process
         - If the institution is registered already they get forwarded to the account page
         - otherwise, store the contact info with the selected_institution in the session (NOT the DB)
    """
    (institution, response) = _get_selected_institution(request)
    if response: return response
        
    # Provide the Contact Information Form
    reg_form = RegistrationForm(instance=institution)

    if request.method == "POST":
        reg_form = RegistrationForm(request.POST, instance=institution)

        if reg_form.is_valid():
            
            institution = reg_form.save(commit=False)
            request.session['selected_institution'] = institution
            
            # they're done if it's international
            if institution.international:
                institution = register_institution(request.user, institution, "credit", 0, None)
                request.session['selected_institution'] = institution
                return HttpResponseRedirect("/register/survey/")
            
            return HttpResponseRedirect('/register/step3/')
        else:
            flashMessage.send("Please correct the errors below", flashMessage.ERROR)
            
    template = "registration/contact.html"
    context = {'reg_form': reg_form, 'institution': institution}
    return respond(request, template, context)

def reg_payment(request):
    """
        STEP 3: Determine the payment price and process payment for this institution's registration
         - if the institution is registered already they get forwarded to the account page
         - otherwise, collect payment info and store the selected_institution into the DB
   """
    (institution, response) = _get_selected_institution(request)
    if response: return response
    
    # get price
    price = _get_registration_price(institution)
    
    pay_form = PaymentForm()
    pay_later_form = PayLaterForm()
    result = None # Stores the response from the payment gateway

    if request.method == "POST":
        pay_later_form = PayLaterForm(request.POST)

        if pay_later_form.is_valid():
            if not pay_later_form.cleaned_data['confirm']:

                pay_form = PaymentForm(request.POST)
                if pay_form.is_valid():
                    payment_dict = get_payment_dict(pay_form, institution)
                    product_dict = {
                        'price': price,
                        'quantity': 1,
                        'name': "STARS Participant Registration",
                    }

                    result = process_payment(payment_dict, [product_dict], invoice_num=institution.aashe_id)
                    if result.has_key('cleared') and result.has_key('msg'):
                        if result['cleared'] and result['trans_id']:
                            institution = register_institution(request.user, institution, "credit", price, payment_dict)
                            request.session['selected_institution'] = institution
                            return HttpResponseRedirect("/register/survey/")
                        else:
                            flashMessage.send("Processing Error: %s" % result['msg'], flashMessage.ERROR)
                else:
                    flashMessage.send("Please correct the errors below", flashMessage.ERROR)
                    
            else:
                institution = register_institution(request.user, institution, "later", price, None)
                request.session['selected_institution'] = institution
                return HttpResponseRedirect("/register/survey/")
    
    template = "registration/payment.html"
    context = {'pay_form': pay_form, 'pay_later_form': pay_later_form, 'institution': institution, 'is_member': institution.is_member, 'price': price}
    return respond(request, template, context)

def init_submissionset(institution, user, today):
    """
        Initializes a submissionset for an institution and user
        adding the today argument makes this easier to test explicitly
    """
    # Get the current CreditSet
    creditset = CreditSet.objects.get_latest()
    # Submission is due in one year
    deadline = today + timedelta(days=365) # Gives them an extra day on leap years :)
    submissionset = SubmissionSet(creditset=creditset, institution=institution, date_registered=today, submission_deadline=deadline, registering_user=user, status='ps')
    submissionset.save()
    init_credit_submissions(submissionset)
    return submissionset

def register_institution(user, institution, payment_type, price, payment_dict):
    """
        Register an institution for the current credit set:
         - create and store all the necessary registration information
         - send confirmation emails
    """
    
    # Save Institution
    institution.enabled = True
    institution.update_from_iss()
    institution.save()
    
    # Create Admin User
    account = StarsAccount(user=user, institution=institution, user_level='admin', is_selected=False, terms_of_service=True)
    account.save()
    account.select()
    
    # Set up the SubmissionSet
    submissionset = init_submissionset(institution, user, datetime.today())
    
    # Add the institution state so it has an active submission.
    institution.set_active_submission(submissionset)
    
    # Save Payment
    if institution.is_member_institution():
        reason = "member_reg"
    elif institution.international:
        reason = "international"
    else:
        reason = "nonmember_reg"
    payment = Payment(submissionset=submissionset, date=datetime.today(), amount=price, user=user, reason=reason, type=payment_type, confirmation="none")
    payment.save()
    
    # Primary Contact
    subject = "STARS Registration Success: %s" % institution
    email_to = [institution.contact_email]
    
    if user.email != institution.contact_email:
        email_to.append(user.email)
    
    # Confirmation Email
    if institution.international:
        et = EmailTemplate.objects.get(slug='welcome_international_pilot')
        email_context = {'institution': institution}
    elif payment.type == 'later':
        et = EmailTemplate.objects.get(slug='welcome_liaison_unpaid')
        email_context = {'payment': payment,}
    else:
        et = EmailTemplate.objects.get(slug='welcome_liaison_paid')
        email_context = {"institution": institution, 'payment': payment, 'payment_dict': payment_dict}
    
    et.send_email(email_to, email_context)
                
    # Executive Contact
    email_to = [institution.executive_contact_email,]
    if institution.international:
        et = EmailTemplate.objects.get(slug='welcome_international_pilot_ec')
    else:
        et = EmailTemplate.objects.get(slug="welcome_exec")
    email_context = {"institution": institution}
    et.send_email(email_to, email_context)
        
    return institution
    
class RegistrationSurveyView(AuthenticatedMixin, FormActionView):
    """
        A survey step after users complete the registration process
    """
    
    def render(self, request, *args, **kwargs):
        
        if not self.get_institution(request):
            flashMessage.send("No Registered Institution Selected")
            return HttpResponseRedirect("/register/step1/")
        
        return super(RegistrationSurveyView, self).render(request, *args, **kwargs)
    
    def save_form(self, form, request, context):
        """ Updates the resonse with the user and institution before saving """
        rr = form.save(commit=False)
        rr.institution = self.get_institution(request)
        rr.user = request.user
        rr.save()
        # Because I use `commit=False` above, I have to save the m2m separately:
        # # http://docs.djangoproject.com/en/dev/topics/forms/modelforms/#the-save-method
        form.save_m2m()
        
    def get_success_action(self, request, context, form):
        """
            On successful submission of the form, redirect to the registration account page
        """
        self.save_form(form, request, context)

        return HttpResponseRedirect('/register/account/')
    
    def get_institution(self, request):

        # Get the user's current account information. First try the registration selected_institution from the session...
        institution = request.session.get('selected_institution', None)

        if not institution:  # If that's not there, we'll try to get it from the user's accounts (from DB)
            account = request.user.account
            if account and account.institution.is_registered():
                institution = account.institution
                request.session['selected_institution'] = institution
        
        return institution
        
survey = RegistrationSurveyView("registration/survey.html", RegistrationSurveyForm,  form_name='object_form', instance_name='institution')
    
def reg_account(request):
    """
        Displays the user's account page.
        If a user is associated with multiple institutions provide a selection option
    """
    response = _confirm_login(request)
    if response: return response
    
    # Get the user's current account information. First try the registration selected_institution from the session...
    institution = request.session.get('selected_institution', None)
    
    if not institution:  # If that's not there, we'll try to get it from the user's accounts (from DB)
        account = request.user.account
        if account and account.institution.is_registered():
            institution = account.institution
            request.session['selected_institution'] = institution
        else:            # can't find any registered institution for this user...
            flashMessage.send("No Registered Institution Selected")
            return HttpResponseRedirect("/register/step1/")
            
    # Determine the amount due
    amount_due = 0
    try:
        payments = Payment.objects.filter(submissionset__institution=institution)
        for payment in payments:
            if payment.type == 'later':
                amount_due = payment.amount
    except:
        watchdog.log("Registration Account", "No payment found for institution.", watchdog.ERROR)
    
    template = "registration/account.html"
    context = {'institution': institution, 'amount_due': amount_due}
    return respond(request, template, context)
    
def get_payment_dict(pay_form, institution):
    """ Extracts the payment dictionary for process_payment from a given form and institution """
    
    cc = pay_form.cleaned_data['card_number']
    l = len(cc)
    if l >= 4:
        last_four = cc[l-4:l]
    else:
        last_four = None
    
    payment_dict = {
        'name_on_card': pay_form.cleaned_data['name_on_card'],
        'cc_number': pay_form.cleaned_data['card_number'],
        'exp_date': pay_form.cleaned_data['exp_month'] + pay_form.cleaned_data['exp_year'],
        'cv_number': pay_form.cleaned_data['cv_code'],
        'billing_address': pay_form.cleaned_data['billing_address'],
        'billing_address_line_2': pay_form.cleaned_data['billing_address_line_2'],
        'billing_city': pay_form.cleaned_data['billing_city'],
        'billing_state': pay_form.cleaned_data['billing_state'],
        'billing_zipcode': pay_form.cleaned_data['billing_zipcode'],
        'country': "USA",
        'billing_firstname': institution.contact_first_name,
        'billing_lastname': institution.contact_last_name,
        'billing_email': institution.contact_email,
        'description': "%s STARS Registration (%s)" % (institution.name, datetime.now().isoformat()),
        'company': institution.name,
        'last_four': last_four,
    }
    
    if is_canadian_zipcode(pay_form.cleaned_data['billing_zipcode']):
        payment_dict['country'] = "Canada"
        
    return payment_dict

def process_payment(payment_dict, product_list, invoice_num=None, server=None, login=None, key=None):
    """
        Connects to Authorize.net and processes a payment based on the payment
        information in payment_dict and the product_dict
        payment_dict: {first_name, last_name, street, city, state, zip, country, email, cc_number, expiration_date}
        product_list: [{'name': '', 'price': #.#, 'quantity': #},]
        server, login, and key: optional parameters for Auth.net connections (for testing)

        returns:
            {'cleared': cleared, 'reason_code': reason_code, 'msg': msg, 'conf': "" }
    """
    
    if not server:
        server = settings.AUTHORIZENET_SERVER
    if not login:
        login = settings.AUTHORIZENET_LOGIN
    if not key:
        key = settings.AUTHORIZENET_KEY
    
    cc = CcProcessor(server=server, login=login, key=key)
    
    total = 0.0
    for product in product_list:
        total += product['price'] * product['quantity']
    result = cc.authorize(
                            amount=str(total),
                            card_num=payment_dict['cc_number'],
                            exp_date=payment_dict['exp_date'],
                            invoice_num=invoice_num,
                            address=payment_dict['billing_address'],
                            city=payment_dict['billing_city'],
                            state=payment_dict['billing_state'],
                            zip=payment_dict['billing_zipcode'],
                            first_name=payment_dict['billing_firstname'],
                            last_name=payment_dict['billing_lastname'],
                            card_code=payment_dict['cv_number'],
                            country=payment_dict['country'],
                            )
    
    if result.response == "approved":
        capture_result = cc.captureAuthorized(trans_id=result.trans_id)
        return {'cleared': True, 'reason_code': None, 'msg': None, 'conf': capture_result.approval_code, 'trans_id': capture_result.trans_id}
    else:
        print >> sys.stderr, "Decline: %s" % result.response_reason
        return {'cleared': False, 'reason_code': None, 'msg': result.response_reason, 'conf': None, 'trans_id': None}

def _confirm_login(request):
    """
        Confirm that request.user is logged in.  
        If not, return an appropriate response, if so, return None
    """
     # Confirm that the user is logged in with their AASHE ID
    if not request.user.is_authenticated():
        template = "registration/login_required.html"
        context = {}
        return respond(request, template, context)
    
    return None

def _get_selected_institution(request):
    """
        Confirm that requesting user is logged in and get their selected institution from the session, if possible:
         - If there are any issues (no institution selected, or selected institution already registered), return an appropriate response.
         - If the user is logged in and has a selected institution, return the institution
        returns (institution, response), one of which is None.
    """
    response = _confirm_login(request)
    if response:
        return None, response
    
    # Confirm that there is an institution in their session
    institution = request.session.get('selected_institution')
    if not institution:
        flashMessage.send("No Institution Selected")
        return None, HttpResponseRedirect('/register/step1/')
        
    # if the institution is registered already, take them to the account page
    try:
        if institution.aashe_id:
            inst = Institution.objects.get(aashe_id=institution.aashe_id)
            if inst.is_registered():   # check for registration in the most recent credit set
                request.session['selected_institution'] = inst
                return None, HttpResponseRedirect("/register/account/")
    except Institution.DoesNotExist:
        pass  # no problem - this is the usual case, institution is not registered, proceed with registration.
   
    return institution, None

def _get_registration_price(institution, new=True):
    """
        Calculates the registration price based on the institution
    """
    price = {'member': 900, 'non': 1400}
    
    discount = 0
    if new:
        start_date = date(year=2011, month=10, day=9)
        end_date = date(year=2011, month=10, day=14)
    
        if date.today() >= start_date and date.today() <= end_date:
            discount = 250
        
    if institution.is_member:
        return price['member'] - discount
    else:
        return price['non'] - discount

