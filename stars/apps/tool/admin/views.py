from datetime import datetime, date
import sys

from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import Context, loader, Template, RequestContext
from django.core.mail import send_mail

from stars.apps.accounts.utils import respond
from stars.apps.accounts import utils as auth_utils
from stars.apps.accounts.decorators import user_is_staff
from stars.apps.helpers import watchdog, flashMessage
from stars.apps.helpers.forms import form_helpers
from stars.apps.helpers.forms.forms import Confirm as ConfirmForm
from stars.apps.institutions.models import Institution
from stars.apps.tool.manage.forms import AdminEnableInstitutionForm
from stars.apps.submissions.models import SubmissionSet, Payment
from stars.apps.tool.admin.forms import PaymentForm
from stars.apps.helpers.forms.views import FormActionView

@user_is_staff
def institutions_search(request):
    """
        Provides a search page for Institutions
    """
    return respond(request, 'tool/admin/institutions/institution_search.html', {})

@user_is_staff
def institutions_list(request):
    """
        A list of latest submissionsets for ALL registered institutions currently participating in STARS.
    """
    
    institutions = Institution.objects.order_by('name')
    saved = False
    
    # Add the latest submission set and payment to each institution
    for institution in institutions:
        institution.enable_form, form_saved = form_helpers.basic_save_form(request, institution, 'enable_%s'%institution.id, AdminEnableInstitutionForm,  flash_message=False)
        saved = saved or form_saved
        institution.submission_set = institution.get_latest_submission(True)
        
    if saved:
        flashMessage.send("Institutions updated successfully.", flashMessage.SUCCESS)
    if institution:
        enable_help_text = institution.enable_form['enabled'].help_text

    template = "tool/admin/institutions/institution_list.html"
    return respond(request, template, {'institution_list':institutions, 'enable_help_text':enable_help_text})
    
@user_is_staff
def select_institution(request, aashe_id):
    """
        The admin tool for selecting a particular institution
    """
    institution = Institution.objects.get(aashe_id=aashe_id)
    if not institution:
        raise Http404("No such institution.")
    
    if auth_utils.change_institution(request, institution):  
        redirect_url = request.GET.get('redirect', settings.MANAGE_INSTITUTION_URL) 
        response = HttpResponseRedirect(redirect_url)
        # special hack to "remember" current institution for staff between sessions
        #  - can't store it in session because it gets overwritten on login, can's store it with account b/c staff don't have accounts.
        #  - ideally, the cookie path would be LOGIN_URL, but the first request we get is from the login redirect url.
        response.set_cookie("current_inst", institution.aashe_id, path=settings.LOGIN_REDIRECT_URL)
        return response
    else:
        flashMessage.send("Unable to change institution to %s - check the log?"%institution, flashMessage.ERROR)
        return HttpResponseRedirect(settings.ADMIN_URL)

@user_is_staff
def latest_payments(request):
    """
        A list of institutions with their latest payment
    """
    # Select the latest payment for each institution -
    # The query I want is something like:
    # SELECT payment, submissionset__institution FROM Payment GROUP BY submissionset__institution__id  HAVING  payment.date = MAX(payment.date)
    # But I can't figure out how to get Django to do this in single query - closest I can come is:
    #    institutions = Institution.objects.annotate(latest_payment=Max('submissionset__payment__date'))
    #  but that annotates each institution with the latest payment DATE - not the Payment object :-(  So... 
    # - First a query to get the id's for latest payment for each institution
    # - Then a query to get the actual objects - seems like there must be a direct way here....  
    from django.db.models import Max
    payment_ids = Payment.objects.values('submissionset__institution').annotate(latest_payment=Max('date')).values('id')
    payments = Payment.objects.filter(id__in=[x['id'] for x in payment_ids]).order_by('-date').select_related('submissionset', 'submissionset__institution')

    template = "tool/admin/payments/latest.html"
    return respond(request, template, {'payment_list':payments})


@user_is_staff
def institution_payments(request, institution_id):
    """
        Display a detailed list of payments made by the institution
    """
    institution = get_object_or_404(Institution, id=institution_id)
    
    payment_list = Payment.objects.filter(submissionset__institution=institution).order_by('-date')

    # Build the form for adding a new payment for staff, if there is active submission
    active_submission = institution.get_active_submission()
    if active_submission and request.user.is_staff:
        new_payment = Payment(submissionset=active_submission, user=request.user, date=datetime.today())
        new_payment_form = PaymentForm(instance=new_payment, prefix='new_payment')
        new_payment_form.add_user(request.user)
        new_payment_url = active_submission.get_add_payment_url()
    else:
        new_payment_form = None
        new_payment_url = None
        
    context = {'institution': institution,
               'payment_list': payment_list, 
               'active_submission':active_submission,
               'new_payment_url':new_payment_url,
               'new_payment_form':new_payment_form,
              }
    return respond(request, 'tool/admin/payments/detail_list.html', context)
    

@user_is_staff
def add_payment(request, institution_id, submissionset_id):
    """
        Process a form for adding a new payment against the given submission set
    """
    submissionset = get_object_or_404(SubmissionSet, institution__id=institution_id, id=submissionset_id)
    
#    if not active_submission:
#            raise PermissionDenied("A Submission Set must be added before you can add a payment.")
    payment = Payment(submissionset=submissionset, user=request.user, date=datetime.today())
        
    # Build and process the form for adding the payment...
    (payment_form,saved) = form_helpers.basic_save_form(request, payment, 'new_payment', PaymentForm)
    if saved:
        return HttpResponseRedirect(payment.get_admin_url())

    payment_form.add_user(request.user)

    context = {'payment': payment, 'object_form':payment_form, 'title':'New Payment'}
    return respond(request, 'tool/admin/payments/edit.html', context)

@user_is_staff
def edit_payment(request, payment_id):
    """
        Process a form for editing payment details
    """
    payment = get_object_or_404(Payment, id=payment_id)
        
    # Build and process the form for adding or modifying the payment...
    (payment_form,saved) = form_helpers.basic_save_form(request, payment, 'payment', PaymentForm)
    if saved:
        return HttpResponseRedirect(payment.get_admin_url())

    payment_form.add_user(request.user)

    context = {'payment': payment, 'object_form':payment_form, 'title':'Edit Payment Details'}
    return respond(request, 'tool/admin/payments/edit.html', context)
    
@user_is_staff
def send_receipt(request, payment_id):
    """
        Tool allowing staff to send receipts for payments to the STARS Liaison
    """
    payment = get_object_or_404(Payment, id=payment_id)
    
class PaymentReceiptView(FormActionView):
    
    def get_success_action(self, request, context, form):

        send_mail(  context['subject'],
                    context['message'],
                    settings.EMAIL_HOST_USER,
                    [context['payment'].submissionset.institution.contact_email,],
                    fail_silently=False
                    )

        return render_to_response("tool/admin/payments/receipt_confirm.html", RequestContext(request, context))
    
    def get_extra_context(self, request, *args, **kwargs):
        """ Extend this method to add any additional items to the context """
        
        print >> sys.stderr, "my_kwargs: %s" % kwargs
        
        payment = get_object_or_404(Payment, id=kwargs['payment_id'])
        t = loader.get_template('tool/admin/payments/receipt.txt')
        message = t.render(Context({'payment': payment, 'today': date.today()}))
        subject = "STARS Payment Receipt"
        
        return {'payment': payment, 'message': message, 'subject': subject}

send_receipt = PaymentReceiptView("tool/admin/payments/receipt.html", ConfirmForm, has_upload=True, form_name='object_form',)

@user_is_staff
def delete_payment(request, payment_id):
    """
        Confirmation for deleting a Payment
    """
    payment = get_object_or_404(Payment, id=payment_id)
    
    (form, deleted) = form_helpers.confirm_delete_form(request, payment)       
    if deleted:
        watchdog.log('Inst. Admin', "Payment: %s deleted."%payment, watchdog.NOTICE)
        return HttpResponseRedirect(payment.get_admin_url())
    
    return respond(request, 'tool/admin/payments/delete.html', {'payment':payment, 'confirm_form': form})
