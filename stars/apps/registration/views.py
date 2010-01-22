from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.forms import widgets
from django.conf import settings
from django.template import Context, loader, Template
from django.core.mail import send_mail

from datetime import datetime, date
import urllib2, re
from xml.etree.ElementTree import fromstring

from stars.apps.institutions.models import Institution, _query_member_list
from stars.apps.registration.forms import *
from stars.apps.auth.utils import respond, connect_member_list
from stars.apps.helpers import watchdog, flashMessage
from stars.apps.tool.admin.watchdog.models import ERROR
from stars.apps.auth import xml_rpc
from stars.apps.registration.globals import *
from stars.apps.submissions.models import *
from stars.apps.credits.models import CreditSet
        
def reg_select_institution(request):
    """
        STEP 1: User selects an institution from the pull-down menu
         - store the selected institution in the Session (not the DB), and move on to the next step
    """
    response = _confirm_login(request)
    if response: return response
    
    # Get the user's institution from AASHE ID
    institution_id = None    # @TODO get this from Drupal when salesforce comes online
    institution_list = []
    institution_list_lookup = {}
    
    # Get the list of schools as choices
    db = connect_member_list()
    cursor = db.cursor()
    institution_query = """
        SELECT account_num, name, city, state
        FROM `members`
        WHERE (sector = 'Campus' OR organization_type = "System Office")
        and city IS NOT NULL
        and state IS NOT NULL
        ORDER BY name
    """
    cursor.execute(institution_query)
    institution_list = []
    institution_list_lookup = {}
    for row in cursor.fetchall():
        institution_list.append((row[0], "%s, %s, %s" % (row[1], row[2], row[3])))
        institution_list_lookup[row[0]] = row[1]
    db.close()
    
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
            if selected_institution and selected_institution.aashe_id == institution.aashe_id:
                pass
            else:
                request.session['selected_institution'] = institution
            return HttpResponseRedirect('/register/step2/')
        else:
            e = form.errors
            # This SHOULDN'T happen!
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
                            return HttpResponseRedirect("/register/account/")
                        else:
                            flashMessage.send("Processing Error: %s" % result['msg'], flashMessage.ERROR)
                else:
                    flashMessage.send("Please correct the errors below", flashMessage.ERROR)
                    
            else:
                institution = register_institution(request.user, institution, "later", price, None)
                request.session['selected_institution'] = institution
                return HttpResponseRedirect("/register/account/")
    
    template = "registration/payment.html"
    context = {'pay_form': pay_form, 'pay_later_form': pay_later_form, 'institution': institution, 'is_member': is_member, 'price': price}
    return respond(request, template, context)


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
    
    # Create SubmissionSet
    # Get the current CreditSet
    creditset = CreditSet.get_latest_creditset()
    deadline = date(year=2011, day=31, month=1)   # @todo: hmmmm - the default deadline should be stored with the creditset, no?
    submissionset = SubmissionSet(creditset=creditset, institution=institution, date_registered=datetime.today(), submission_deadline=deadline, registering_user=user, status='ps')
    submissionset.save()
    
    # Add the institution state so it has an active submission.
    institution.set_active_submission(submissionset)
    
    # Save Payment
    payment = Payment(submissionset=submissionset, date=datetime.today(), amount=price, user=user, reason='reg', type=payment_type, confirmation="none")
    payment.save()
    
    # Send Confirmation Emails
    
    cc_list = ['stars@aashe.org', 'allison@aashe.org']
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
                email_to + cc_list,
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
        account = StarsAccount.get_selected_account(request.user)
        if account and account.institution.is_registered(): 
            institution = account.institution
            request.session['selected_institution'] = institution
        else:            # can't find any registered institution for this user...
            flashMessage.send("No Registered Institution Selected")
            return HttpResponseRedirect("/register/step1/")
            
    # Determine the amount due
    amount_due = 0
    try:
        payment = Payment.objects.filter(submissionset__institution=institution, type='later')[0]
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
    return payment_dict

def process_payment(payment_dict, product_list, test_mode=False, ref_code=None, debug=False):
    """
        Connects to Cybersource and processes a payment based on the payment
        information in payment_dict and the product_dict
        payment_dict: {first_name, last_name, street, city, state, zip, country, email, cc_number, expiration_date}
        product_dict: [{product_name, product_price, product_quanity}]

        returns:
            {'cleared': cleared, 'reason_code': reason_code, 'msg': msg)
    """

    ref = "my_ref_code"
    if ref_code:
        ref = ref_code

    account = {
        "merchant_id": settings.CYBERSOURCE_MERCHANT_ID,
        "password": settings.CYBERSOURCE_SOAP_KEY,
    }

    t = loader.get_template('registration/cybersource/request.xml')
    c = Context({
        "account": account,
        "ref_code": ref,
        "payment_dict": payment_dict,
        "product_list": product_list,
    })
    request = t.render(c)
    if debug:
        print request
        print """
        **
        CONNECTING
        **
        """

    connection_url = settings.CYBERSOURCE_URL
    if test_mode:
        connection_url = settings.CYBERSOURCE_TEST_URL
    conn = urllib2.Request(url=connection_url, data=request)

    try:
        f = urllib2.urlopen(conn)
    except urllib2.HTTPError, e:
        # we probably didn't authenticate properly
        # make sure the 'v' in your account number is lowercase
        if debug:
            print e.code
            print e.read()
        return({'cleared': False, 'reason_code': '999', 'msg': 'Problem parsing results'})

    all_results = f.read()
    tree = fromstring(all_results)
    parsed_results = tree.getiterator('{urn:schemas-cybersource-com:transaction-data-1.26}reasonCode')
    try:
        reason_code = parsed_results[0].text
    except KeyError:
        return({'cleared': False, 'reason_code': '999', 'msg': 'Problem parsing results'})

    if CYBERSOURCE_RESPONSE_DICT.has_key(reason_code):
        response_text = CYBERSOURCE_RESPONSE_DICT[reason_code]
    else:
        response_text = 'Unknown failure'
    if reason_code == '100':
        return({'cleared': True, 'reason_code': reason_code, 'msg': response_text})
    else:
        return({'cleared': False, 'reason_code': reason_code, 'msg': response_text})

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

