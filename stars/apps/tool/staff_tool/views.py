from datetime import date
from logging import getLogger
from logical_rules.mixins import RulesMixin
from django_async_download.views import StartExportView, DownloadExportView

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.db.models import Min
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, ListView, TemplateView

from stars.apps.accounts.utils import respond
from stars.apps.accounts.decorators import user_is_staff
from stars.apps.institutions.models import (Institution,
                                            SubscriptionPayment,
                                            Subscription)
from stars.apps.institutions.views import SortableTableView
from stars.apps.submissions.models import SubmissionSet
from stars.apps.tool.staff_tool.forms import PaymentForm
from stars.apps.tool.mixins import InstitutionToolMixin
from stars.apps.third_parties.models import ThirdParty
from stars.apps.tasks.notifications import add_months

from tasks import build_accrual_report_csv

logger = getLogger('stars.request')


@user_is_staff
def institutions_search(request):
    """
        Provides a search page for Institutions
    """
    return respond(request, 'tool/admin/institutions/institution_search.html',
                   {})


@user_is_staff
def select_institution(request, id):
    """
        The admin tool for selecting a particular institution
    """
    institution = Institution.objects.get(id=id)
    if not institution:
        raise Http404("No such institution.")
    redirect_url = request.GET.get('redirect',
                                    reverse('tool-summary',
                                    args=(institution.slug,)))
    return HttpResponseRedirect(redirect_url)

# @user_is_staff
# def latest_payments(request):
#     """
#         A list of institutions with their latest payment
#     """
#     # Select the latest payment for each institution -
#     # The query I want is something like:
#     # SELECT payment, submissionset__institution FROM Payment GROUP BY submissionset__institution__id  HAVING  payment.date = MAX(payment.date)
#     # But I can't figure out how to get Django to do this in single query - closest I can come is:
#     #    institutions = Institution.objects.annotate(latest_payment=Max('submissionset__payment__date'))
#     #  but that annotates each institution with the latest payment DATE - not the Payment object :-(  So...
#     # - First a query to get the id's for latest payment for each institution
#     # - Then a query to get the actual objects - seems like there must be a direct way here....
#     from django.db.models import Max
# #    payment_ids = Payment.objects.values('submissionset__institution').annotate(latest_payment=Max('date')).values('id')
#     payments = Payment.objects.all().order_by('-date').select_related('submissionset', 'submissionset__institution')
#
#     template = "tool/admin/payments/latest.html"
#     return respond(request, template, {'payment_list':payments})


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


@user_is_staff
def financial_report(request):
    """
        Provide a quick summary for board reports
    """

    d = today = date.today()
    participants_today = Subscription.objects.filter(start_date__lte=d).filter(end_date__gte=d).count()
    d = last_year = add_months(d, -12)
    participants_last_year = Subscription.objects.filter(start_date__lte=d).filter(end_date__gte=d).count()

    d = date(year=2009, month=10, day=1)
    tbl = []
    while d <= date.today():

        subs = Subscription.objects.filter(start_date__lte=d).filter(end_date__gte=d)

        revenue = 0
        payments = SubscriptionPayment.objects.filter(date__year=d.year).filter(date__month=d.month)
        for p in payments:
            revenue += p.amount

        participants = subs.count()

        tbl.append({
            'date': add_months(d, -1),
            'participants': participants,
            'revenue': revenue})

        d = add_months(d, 1)

    context = {
        'object_list': tbl,
        'today': today,
        'participants_today': participants_today,
        'last_year': last_year,
        'participants_last_year': participants_last_year}
    template = "tool/admin/reports/financial.html"
    return respond(request, template, context)


class ReportMixin(object):

    def update_logical_rules(self):
        super(SubscriptionPaymentBaseMixin, self).update_logical_rules()
        self.add_logical_rule({
            'name': 'user_is_staff',
            'param_callbacks': [('user', 'get_request_user')],
        })


class AccrualReport(ReportMixin, ListView):

    model = SubscriptionPayment
    template_name = 'tool/admin/reports/accrual_report.html'

    def get_queryset(self):
        year = self.request.GET.get('year', 2015)
        try:
            y = int(year)
        except:
            y = 2015
        qs = SubscriptionPayment.objects.all()
        qs = qs.filter(date__year=y).order_by("date")
        return qs

    def get_context_data(self, **kwargs):
        _c = super(AccrualReport, self).get_context_data(**kwargs)
        year = self.request.GET.get('year', 2015)
        try:
            y = int(year)
        except:
            y = 2015
        _c['year'] = y
        _c['today'] = date.today()
        return _c


class AccrualExcelView(ReportMixin, StartExportView):
    """
        Populates the download modal and triggers task
    """
    export_method = build_accrual_report_csv
    download_url_name = "accrual_download"

    def get_task_params(self):
        return self.kwargs['year']

    def get_download_url(self, task):
        """ Useful if your download url will be dynamic """
        return reverse(
            self.download_url_name,
            args=[self.kwargs['year'], task])


class AccrualExcelDownloadView(ReportMixin, DownloadExportView):
    """
        Returns the result of the task (hopefully an excel export)
    """
    mimetype = 'text/csv'
    extension = "csv"

    def get_filename(self):
        return "%s_Accrual_Report" % self.kwargs['year']


class InstitutionList(SortableTableView):
    """
        A quick report on registration for Jillian


        Institution Name
        Reg date
        Renewal Date
        Submission date
    """
    template_name = "tool/admin/institutions/institution_list.html"

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
                        'key': 'rating',
                        'sort_field': 'current_rating',
                        'title': 'Rating',
                    },
                    {
                        'key': 'version',
                        'sort_field': 'current_submission__creditset__version',
                        'title': 'Version',
                    },
                    {
                        'key': 'participation',
                        'sort_field': 'is_participant',
                        'title': 'Access Level',
                    },
                    {
                        'key': 'contact_email',
                        'sort_field': 'contact_email',
                        'title': 'Liaison',
                    },
                    {
                        'key': 'submission',
                        'sort_field': 'rated_submission__date_submitted',
                        'title': 'Submission Date',
                    },
                    # {
                    #     'key':'subscription',
                    #     'sort_field':'current_subscription__start_date',
                    #     'title':'Subscription',
                    # },
              ]

    def get_queryset(self):
        return Institution.objects.annotate(reg_date=Min('subscription__start_date')).select_related()


class SubscriptionPaymentBaseMixin(InstitutionToolMixin):

    model = SubscriptionPayment
    form_class = PaymentForm
    template_name = 'tool/manage/payment_edit.html'

    def update_logical_rules(self):
        super(SubscriptionPaymentBaseMixin, self).update_logical_rules()
        self.add_logical_rule({
                'name': 'user_is_staff',
                'param_callbacks': [('user', 'get_request_user')],
        })

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(SubscriptionPaymentBaseMixin, self).get_form_kwargs()
        kwargs.update({
                        'current_user':
                            self.request.user
                        })
        return kwargs

    def get_success_url(self):
        return reverse('institution-payments',
                kwargs={'institution_slug': self.get_institution().slug})


class AddSubscriptionPayment(SubscriptionPaymentBaseMixin, CreateView):

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(AddSubscriptionPayment, self).get_form_kwargs()
        kwargs.update({
                        'instance':
                            SubscriptionPayment(subscription=self.get_subscription(),
                                                date=date.today())
                        })
        return kwargs

    def form_valid(self, form):
        """
            Update the subscription before responding
        """
        self.object = form.save()
        subscription = self.get_subscription()
        amount_paid = self.object.amount
        if subscription.amount_due < amount_paid:
            logger.error("Payment is greater than amount due for: %s"
                           % subscription)
        if subscription.amount_due >= amount_paid:
            if subscription.amount_due > amount_paid:
                logger.info("Payment is less than amount due for: %s"
                               % subscription)
            subscription.amount_due -= amount_paid
            if subscription.amount_due == 0:
                subscription.paid_in_full = True
            subscription.save()

        return super(AddSubscriptionPayment, self).form_valid(form)


class EditSubscriptionPayment(SubscriptionPaymentBaseMixin, UpdateView):

    def get_object(self):
        return self.get_payment()
