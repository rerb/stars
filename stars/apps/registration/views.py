from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.forms import widgets
from django.conf import settings
from django.template import Context, loader, Template
from django.core.mail import send_mail

from datetime import datetime, date, timedelta
import urllib2, re, sys
from xml.etree.ElementTree import fromstring

from stars.apps.institutions.models import Institution, _query_iss_orgs
from stars.apps.registration.forms import *
from stars.apps.registration.utils import is_canadian_zipcode, is_usa_zipcode
from stars.apps.auth.utils import respond, connect_iss
from stars.apps.helpers import watchdog, flashMessage
from stars.apps.tool.admin.watchdog.models import ERROR
from stars.apps.tool.my_submission.views import _get_active_submission
from stars.apps.auth import xml_rpc
from stars.apps.registration.globals import *
from stars.apps.submissions.models import *
from stars.apps.credits.models import CreditSet
from stars.apps.helpers.forms.views import FormActionView
from stars.apps.auth.mixins import AuthenticatedMixin

from zc.authorizedotnet.processing import CcProcessor
from zc.creditcard import (AMEX, DISCOVER, MASTERCARD, VISA, UNKNOWN_CARD_TYPE)


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
    for inst in _query_iss_orgs():
        if inst['city'] and inst['state']:
            institution_list.append((inst['id'], "%s, %s, %s" % (inst['name'], inst['city'], inst['state'])))
        else:
            institution_list.append((inst['id'], inst['name']))
        institution_list_lookup[inst['id']] = inst['name']
    
    # Generate the school choice form
    form = RegistrationSchoolChoiceForm()
    if request.method == 'POST':
        form = RegistrationSchoolChoiceForm(request.POST)
        if form.is_valid():
            aashe_id = form.cleaned_data['aashe_id']
            name = institution_list_lookup[aashe_id]
            institution = Institution(aashe_id=aashe_id, name=name)
            # If they've already got this institution in their session don't overwrite it
            # it might have contact info
            selected_institution = request.session.get('selected_institution')
            if not selected_institution or selected_institution.aashe_id != institution.aashe_id:
                selected_institution = institution
                
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
            return HttpResponseRedirect('/register/step3/')
        else:
            print >> sys.stderr, reg_form.errors
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
        
    # Determine Membership Status
    is_member = institution.is_member_institution()
    
    # get price
    price = _get_registration_price(is_member)
    
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

                    result = process_payment(payment_dict, [product_dict], ref_code=datetime.now().isoformat())
                    if result.has_key('cleared') and result.has_key('msg'):
                        if result['cleared']:
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
    context = {'pay_form': pay_form, 'pay_later_form': pay_later_form, 'institution': institution, 'is_member': is_member, 'price': price}
    return respond(request, template, context)

def init_submissionset(institution, user, today):
    """
        Initializes a submissionset for an institution and user
        adding the today argument makes this easier to test explicitly
    """
    # Get the current CreditSet
    creditset = CreditSet.get_latest_creditset()
    # Submission is due in one year
    deadline = today + timedelta(days=365) # Gives them an extra day on leap years :)
    submissionset = SubmissionSet(creditset=creditset, institution=institution, date_registered=today, submission_deadline=deadline, registering_user=user, status='ps')
    submissionset.save()
    return submissionset

def register_institution(user, institution, payment_type, price, payment_dict):
    """
        Register an institution for the current credit set:
         - create and store all the necessary registration information
         - send confirmation emails
    """
    
    # Save Institution
    institution.enabled = True
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
    payment = Payment(submissionset=submissionset, date=datetime.today(), amount=price, user=user, reason='reg', type=payment_type, confirmation="none")
    payment.save()
    
    # Send Confirmation Emails
    
    if not settings.DEBUG:
        cc_list = ['stars_staff@aashe.org',]
        allison = ['allison@aashe.org','margueritte.williams@aashe.org']
    else:
        allison = []
        cc_list = []
    
    if user.email != institution.contact_email:
        cc_list.append(user.email)
    
    # Primary Contact
    subject = "STARS Registration Success: %s" % institution
    email_to = [institution.contact_email]
    
    # Confirmation Email
    if payment.type == 'later':
        t = Template(PAY_LATER_EMAIL_TEXT)
    else:
        t = Template(RECEIPT_EMAIL_TEXT)
    c = Context({"institution": institution, 'payment': payment, 'payment_dict': payment_dict})
    message = t.render(c)
    send_mail(  subject,
                message,
                settings.EMAIL_HOST_USER,
                email_to + cc_list + allison,
                fail_silently=False
                )
                
    # Payment Reminder Email
    if payment.type == 'later':
        t = Template(PAY_LATER_REMINDER_TEXT)
        c = Context({'payment': payment,})
        message = t.render(c)
        send_mail(  "STARS Registration",
                    message,
                    settings.EMAIL_HOST_USER,
                    email_to + cc_list,
                    fail_silently=False
                    )
                
    # Executive Contact
    email_to = institution.executive_contact_email
    t = Template(EXEC_EMAIL_TEXT)
    c = Context({"institution": institution})
    message = t.render(c)
    send_mail(  subject,
                message,
                settings.EMAIL_HOST_USER,
                [email_to,] + cc_list,
                fail_silently=False
                )
        
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
        'exp_month': pay_form.cleaned_data['exp_month'],
        'exp_year': pay_form.cleaned_data['exp_year'],
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
        'last_four': last_four
    }
    
    if is_canadian_zipcode(pay_form.cleaned_data['billing_zipcode']):
        payment_dict['country'] = "Canada"
        
    return payment_dict

def process_payment(payment_dict, product_list, invoice_num=None):
    """
        Connects to Cybersource and processes a payment based on the payment
        information in payment_dict and the product_dict
        payment_dict: {first_name, last_name, street, city, state, zip, country, email, cc_number, expiration_date}
        product_list: [{'name': '', 'price': #.#, 'quantity': #},]

        returns:
            {'cleared': cleared, 'reason_code': reason_code, 'msg': msg, 'conf': "" }
    """
    
    cc = CcProcessor(server=settings.AUTHORIZENET_SERVER, login=settings.AUTHORIZENET_LOGIN, key=settings.AUTHORIZENET_KEY)
    
    total = 0.0
    for product in product_list:
        total += product['price'] * product['quantity']
    result = cc.authorize(amount=str(total), card_num=payment_dict['cc_number'], exp_date=payment_dict['exp_date'], invoice_num=invoice_num)
    
    if result.response == "approved":
        return {'cleared': True, 'reason_code': None, 'msg': None, 'conf': result.approval_code, 'trans_id': result.trans_id}
    else:
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
        inst = Institution.objects.get(aashe_id=institution.aashe_id)
        if inst.is_registered():   # check for registration in the most recent credit set
            request.session['selected_institution'] = inst
            return None, HttpResponseRedirect("/register/account/")
    except Institution.DoesNotExist:
        pass  # no problem - this is the usual case, institution is not registered, proceed with registration.
   
    return institution, None

def _get_registration_price(is_member):
    """
        Calculates the registration price based on the 
    """
    deadline = datetime(2010, 1, 1, 3, 0, 0) # January 1st at 3am
    early = {'member': 650, 'non': 1150}
    regular = {'member': 900, 'non': 1400}
    
    if datetime.now() < deadline:   # Early Registration
        price = early
    else:                           # Normal Registration
        price = regular
        
    if is_member:
        return price['member']
    else:
        return price['non']

