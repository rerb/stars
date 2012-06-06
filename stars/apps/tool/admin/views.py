from datetime import datetime, date
import sys

from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import Context, loader, Template, RequestContext
from django.core.mail import send_mail
from django.db.models import Min
from django.utils.decorators import method_decorator

from stars.apps.accounts.utils import respond
from stars.apps.accounts import utils as auth_utils
from stars.apps.accounts.decorators import user_is_staff
from stars.apps.helpers import watchdog, flashMessage
from stars.apps.helpers.forms import form_helpers
from stars.apps.helpers.forms.forms import Confirm as ConfirmForm
from stars.apps.institutions.models import Institution, Subscription, SubscriptionPayment
from stars.apps.institutions.views import SortableTableView
from stars.apps.tool.manage.forms import AdminEnableInstitutionForm
from stars.apps.submissions.models import SubmissionSet
from stars.apps.tool.admin.forms import PaymentForm
from stars.apps.helpers.forms.views import FormActionView
from stars.apps.third_parties.models import ThirdParty

@user_is_staff
def institutions_search(request):
    """
        Provides a search page for Institutions
    """
    return respond(request, 'tool/admin/institutions/institution_search.html', {})

#@user_is_staff
#def institutions_list(request):
#    """
#        A list of latest submissionsets for ALL registered institutions currently participating in STARS.
#    """
#    
#    institution_list = Institution.objects.order_by('name')
#
#    template = "tool/admin/institutions/institution_list.html"
#    return respond(request, template, {'institution_list': institution_list,})
    
@user_is_staff
def select_institution(request, id):
    """
        The admin tool for selecting a particular institution
    """
    institution = Institution.objects.get(id=id)
    if not institution:
        raise Http404("No such institution.")
    
    if auth_utils.change_institution(request, institution):  
        redirect_url = request.GET.get('redirect', settings.MANAGE_INSTITUTION_URL) 
        response = HttpResponseRedirect(redirect_url)
        # special hack to "remember" current institution for staff between sessions
        #  - can't store it in session because it gets overwritten on login, can's store it with account b/c staff don't have accounts.
        #  - ideally, the cookie path would be LOGIN_URL, but the first request we get is from the login redirect url.
        response.set_cookie("current_inst", institution.id, path=settings.LOGIN_REDIRECT_URL)
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
#    payment_ids = Payment.objects.values('submissionset__institution').annotate(latest_payment=Max('date')).values('id')
    payments = Payment.objects.all().order_by('-date').select_related('submissionset', 'submissionset__institution')

    template = "tool/admin/payments/latest.html"
    return respond(request, template, {'payment_list':payments})


@user_is_staff
def overview_report(request):
    """
        Provide a quick summary report
    """
    
    context = {
                "current_participants": Institution.objects.filter(is_participant=True).count(),
                "current_respondents": Institution.objects.filter(is_participant=False).count(),
               }
    
    count = 0
    for i in Institution.objects.all():
        if i.subscription_set.count() == 0:
            count += 1
            
    context["registered_respondents"] = count
    context['third_party_list'] = ThirdParty.objects.all()
    
    context['snapshot_count'] = SubmissionSet.objects.filter(status='f').count()
    
    c = 0
    for i in Institution.objects.all():
        if i.submissionset_set.filter(status='f').count() > 0:
            c += 1
    context['institutions_with_snapshots'] = c

    template = "tool/admin/reports/quick_overview.html"
    
    return respond(request, template, context)


class InstitutionList(SortableTableView):
    """
        A quick report on registration for Jillian
        
        
        Institution Name
        Reg date
        Renewal Date
        Submission date
    """
    
    @method_decorator(user_is_staff)
    def render(self, request, *args, **kwargs):
        return super(InstitutionList, self).render(request, *args, **kwargs)
    
    default_key = 'name'
    default_rev = '-'
    secondary_order_field = 'name'
    columns = [
                    {
                        'key': 'name',
                        'sort_field': 'name',
                        'title': 'Institution',
                    },
                    {
                        'key': 'version',
                        'sort_field': 'current_submission__creditset__version',
                        'title': 'Version',
                    },
                    {
                        'key': 'participation',
                        'sort_field': 'is_participant',
                        'title': 'Participant?',
                    },
                    {
                        'key': 'reg_date',
                        'sort_field': 'reg_date',
                        'title': 'Registered',
                    },
                    {
                        'key': 'rating',
                        'sort_field': 'current_rating',
                        'title': 'Rating',
                    },
                    {
                        'key': 'submission',
                        'sort_field': 'rated_submission__date_submitted',
                        'title': 'Submission Date',
                    },
                    {
                        'key':'subscription',
                        'sort_field':'current_subscription__start_date',
                        'title':'Subscription',
                    },
              ]
              
    def get_queryset(self):
        return Institution.objects.annotate(reg_date=Min('subscription__start_date')).select_related()
    
institutions_list = InstitutionList(template="tool/admin/institutions/institution_list.html")

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
def add_subscriptionpayment(request, institution_id, subscription_id):
    """
        Process a form for adding a new payment against the given submission set
    """
    institution = get_object_or_404(Institution, id=institution_id)
    subscription = get_object_or_404(Subscription, institution__id=institution_id, id=subscription_id)
    payment = SubscriptionPayment(subscription=subscription, user=request.user, date=datetime.today(), amount=subscription.amount_due)
        
    # Build and process the form for adding the payment...
    (payment_form,saved) = form_helpers.basic_save_form(request, payment, 'new_payment', PaymentForm)
    if saved:
        # update subscription payment status
        if payment.amount == subscription.amount_due:
            subscription.paid_in_full = True
            subscription.amount_due = 0
            subscription.save()
        else:
            subscription.amount_due -= payment.amount
            subscription.save()
            
        return HttpResponseRedirect("/tool/manage/payments/")

    payment_form.add_user(request.user)

    context = {'payment': payment, 'object_form':payment_form, 'title':'New Payment', 'institution': institution}
    return respond(request, 'tool/manage/payment_edit.html', context)

@user_is_staff
def edit_subscriptionpayment(request, institution_id, payment_id):
    """
        Process a form for editing payment details
    """
    institution = get_object_or_404(Institution, id=institution_id)
    payment = get_object_or_404(SubscriptionPayment, subscription__institution__id=institution_id, id=payment_id)
    old_amount = payment.amount
        
    # Build and process the form for adding or modifying the payment...
    (payment_form,saved) = form_helpers.basic_save_form(request, payment, 'payment', PaymentForm)
    if saved:
        return HttpResponseRedirect("/tool/manage/payments/")

    payment_form.add_user(request.user)

    context = {'payment': payment, 'object_form':payment_form, 'title':'Edit Payment Details', 'institution': institution}
    return respond(request, 'tool/manage/payment_edit.html', context)
    
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
