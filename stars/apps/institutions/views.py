from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.views.generic.simple import direct_to_template
from django.core.exceptions import PermissionDenied
from django.utils.functional import curry
from django.forms.models import inlineformset_factory

import sys, re
from datetime import date
from recaptcha.client import captcha

from stars.apps.accounts.utils import respond
from stars.apps.accounts.mixins import InstitutionAccessMixin
from stars.apps.credits.models import CreditSet
from stars.apps.submissions.models import *
from stars.apps.institutions.models import Institution, StarsAccount
from stars.apps.institutions.forms import *
from stars.apps.institutions.rules import institution_has_export
from stars.apps.helpers.forms.views import TemplateView, FormActionView, MultiFormView
from stars.apps.credits.views import CreditNavMixin
from stars.apps.notifications.models import EmailTemplate

class SortableTableView(TemplateView):
    """
        A class-based view for displaying a sortable list of objects
        The extending class should set two property variables: `columns` and `default_key`
        And override the `get_queryset` method
    """
    
    columns = None # This is coupled to the template :(
    default_key = None # The default column to sort on
    
    def __init__(self, *args, **kwargs):
        
        # make sure that the extending class has defined the required properties.
        assert (self.columns and self.default_key), "Must `colums` and `default_key` when extending this class"
        return super(SortableTableView, self).__init__(*args, **kwargs)
    
    @property
    def __name__(self):
        "Added to get DjDT to work"
        return self.__class__.__name__
    
    def get_context(self, request, *args, **kwargs):
        """ Add/update any context variables """
        context = {'sort_columns': self.columns, 'default_key': self.default_key}
        
        (context['sort_key'], context['rev'], context['object_list']) = self.get_object_list(request)
        
        return context
        
    def get_queryset(self):
        """ Gets the base queryset for the object_list """
        raise NotImplementedError, "Please override this method"
        
    def get_object_list(self, request):
        """
            Returns a queryset based on the GET Parameters
            Also returns the selected `sort_key`
            and `rev`, a "-" or empty string indicating the reverse sort order
        """
        
        sort_key = None
        asc = ""
        rev = ""
        queryset = self.get_queryset()
        
        if request.GET.has_key('sort'):
            if request.GET['sort'][0] == '-':
                asc = '-'
                rev = ''
                sort_key = request.GET['sort'][1:]
            else:
                asc = ''
                rev = '-'
                sort_key = request.GET['sort']
        else:
            sort_key = self.default_key
            rev = self.default_rev
            if rev == '':
                asc = '-'
            
        for col in self.columns:
            if col['key'] == sort_key:
                queryset = queryset.order_by("%s%s" % (asc, col['sort_field']), self.secondary_order_field)
        
        return (sort_key, rev, queryset)
        
class SortableTableViewWithInstProps(SortableTableView):
    """ Extends SortableTableView to include institutional properties from the list"""
    
    def get_context(self, request, *args, **kwargs):
        """ update the context with the # of members and charter participants """
        
        _context = super(SortableTableViewWithInstProps, self).get_context(request, *args, **kwargs)

        inst_list = []
        inst_count = 0
        member_count = 0
        charter_count = 0
        pilot_count = 0
        international_count = 0
        for i in self.get_queryset():
            if i.id not in inst_list:
                inst_list.append(i.id)
                inst_count += 1
                if i.charter_participant:
                    charter_count += 1
                if i.is_member:
                    member_count += 1
                if i.is_pilot_participant:
                    pilot_count += 1
                if i.international:
                    international_count += 1
            
        _context['inst_count'] = inst_count
        _context['member_count'] = member_count
        _context['charter_count'] = charter_count
        _context['pilot_count'] = pilot_count
        _context['international_count'] = international_count
        return _context
    

class ActiveInstitutions(SortableTableViewWithInstProps):
    """
        Extending SortableTableView to show a sortable list of all active participants
    """

    default_key = 'name'
    default_rev = '-'
    secondary_order_field = 'name'
    columns = [
                    {
                        'key': 'name',
                        'sort_field': 'name',
                        'title': 'Institution',
                    },
                    # {
                    #     'key': 'status',
                    #     'sort_field': 'status',
                    #     'title': 'Status',
                    # },
                    {
                        'key': 'rating',
                        'sort_field': 'current_rating',
                        'title': 'Rating',
                    },
#                    {
#                        'key': 'version',
#                        'sort_field': 'creditset__version',
#                        'title': 'Version',
#                    },
                    # {
                    #     'key': 'date_registered',
                    #     'sort_field': 'date_registered',
                    #     'title': 'Date Registered',
                    # },
              ]
    
    def get_queryset(self):
        """
            Get the submission sets for all institutions
            
            Institutions shouldn't show up twice
                - rated institutions show their rating
                - unrated institutions show their next due date
        """
        return Institution.objects.filter(is_participant=True)
#        return SubmissionSet.objects.published().select_related('institution')
    
    
class RatedInstitutions(SortableTableViewWithInstProps):
    """
        Extending SortableTableView to show a sortable list of all active submissionsets
    """

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
                        'sort_field': 'rated_submission__creditset__version',
                        'title': 'Version',
                    },
                    {
                        'key': 'rating',
                        'sort_field': 'rating',
                        'title': 'Rating',
                    },
                    {
                        'key':'date_submitted',
                        'sort_field':'rated_submission__date_submitted',
                        'title':'Submission Date',
                    },
              ]
              
    def get_queryset(self):
        return Institution.objects.get_rated().select_related('rated_submission').select_related('rated_submission__creditset')

"""
    INSTITUTIONAL REPORTS
"""

class InstitutionScorecards(TemplateView):
    """
        Provides a list of available reports for an institution
        
        Unrated SubmissionSets will be displayed to participating users only.
    """
    def get_context(self, request, *args, **kwargs):
        
        institution = get_object_or_404(Institution, slug=kwargs['institution_slug'])
        
        submission_sets = []
        qs = institution.submissionset_set.filter(is_visible=True, is_locked=False)
        if not institution.is_participant:
            # non participants only see rated submissions
            qs = qs.filter(status='r')
        
        for ss in qs:
            if ss.status == 'r':
                submission_sets.append(ss)
            elif request.user.has_perm('admin'):
                submission_sets.append(ss)
            else:
                try:
                    account = StarsAccount.objects.get(institution=institution, user=request.user)
                    if account.has_access_level('observer'):
                        submission_sets.append(ss)
                except:
                    pass
                    
        if len(submission_sets) < 1 and not institution.is_participant:
            raise Http404
                
        return {'submission_sets': submission_sets, 'institution': institution}
    
class ScorecardMixin(object):
    
    def get_submissionset_context(self, request, **kwargs):
        """
            Gets all the available contexts associated with a submission from the kwargs
            
            Available keywords:
                - institution_slug
                - submissionset (id or date submitted)
                - category_id
                - subcategory_id
                - credit_id
            
            Refuse access to non 'observer' or higher roles for unrated submissions
        """
        context = {}
        # Get the Institution
        context['user_tied_to_institution'] = False
        context['preview'] = False
        if kwargs.has_key('institution_slug'):
            institution = get_object_or_404(Institution, slug=kwargs['institution_slug'])
            context['institution'] = institution
            
            # Check that the user has a StarsAccount for this institution, or is an admin
            if request.user.is_authenticated():
                try:
                    account = StarsAccount.objects.get(institution=institution, user=request.user)
                except StarsAccount.DoesNotExist:
                    account = None
                    
                if account:
                    context['user_tied_to_institution'] = True
                    if account.user_level == 'admin':
                        context['user_is_inst_admin'] = True
                        
                if request.user.is_staff:
                    context['user_tied_to_institution'] = True
                    context['user_is_inst_admin'] = True
            
            # Get the SubmissionSet
            date_re = "^\d{4}-\d{2}-\d{2}$"
            id_re = "^\d+$"
            if kwargs.has_key('submissionset'):
                if re.match(id_re, kwargs['submissionset']):
                    submissionset = get_object_or_404(SubmissionSet, id=kwargs['submissionset'], institution=institution)
                elif re.match(date_re, kwargs['submissionset']):
                    submissionset = get_object_or_404(SubmissionSet, date_submitted=kwargs['submissionset'], institution=institution)
                else:
                    raise Http404
                # if the submissionset isn't rated raise a 404 exception unless the user has preview access
                if submissionset.status != 'r':
                    if context.has_key('user_tied_to_institution'):
                        context['preview'] = True
                    else:
                        raise Http404
                    
                context['submissionset'] = submissionset
                
        category, subcategory, credit = self.get_creditset_selection(request, submissionset.creditset, **kwargs)
        
        # Get the submission objects for each element...
        context['current'] = None
        if category:
            category_submission = get_object_or_404(CategorySubmission, category=category, submissionset=submissionset)
            context['category_submission'] = category_submission
            context['current'] = category
        if subcategory:
            subcategory_submission = get_object_or_404(SubcategorySubmission, category_submission=category_submission, subcategory=subcategory)
            context['subcategory_submission'] = subcategory_submission
            context['current'] = subcategory
        if credit:
            credit_submission = get_object_or_404(CreditUserSubmission, subcategory_submission=subcategory_submission, credit=credit)
            context['credit_submission'] = credit_submission
            context['current'] = credit

        return context
        
    def get_category_url(self, category, url_prefix):
        """ The default link for a category. """
        return "%s%s" % (url_prefix, category.get_browse_url())

    def get_subcategory_url(self, subcategory, url_prefix):
        """ The default link for a category. """
        return "%s%s" % (url_prefix, subcategory.get_browse_url())

    def get_credit_url(self, credit, url_prefix):
        """ The default credit link. """
        return "%s%s" % (url_prefix, credit.get_browse_url())
        
class ScorecardView(ScorecardMixin, CreditNavMixin, TemplateView):
    """
        Browse credits according to submission in the credit browsing view
    """
    @property
    def __name__(self):
        return self.__class__.__name__
    
    def get_context(self, request, *args, **kwargs):
        """ Expects arguments for category_id/subcategory_id/credit_id """
        
        context = self.get_submissionset_context(request, **kwargs)
        
        url_prefix = context['submissionset'].get_scorecard_url()
            
        context['outline'] = self.get_creditset_navigation(context['submissionset'].creditset, url_prefix=url_prefix, current=context['current'])
        
        context['score'] = context['submissionset'].get_STARS_score()
        context['rating'] = context['submissionset'].get_STARS_rating()
        
        return context

class PDFExportView(InstitutionAccessMixin, ScorecardMixin, CreditNavMixin, TemplateView):
    """
        Displays an exported PDF version of the selected report
    """
    
    # Mixin required properties
    access_level = 'observer'
    
    def get_context(self, request, *args, **kwargs):
        """ Expects arguments for category_id/subcategory_id/credit_id """
        
        return self.get_submissionset_context(request, **kwargs)
        
    def render(self, request, *args, **kwargs):
        """ Renders the pdf as a response """
        
        _context = self.get_context(request, *args, **kwargs)
        
        ss = _context['submissionset']
        
        if not institution_has_export(ss.institution):
            raise PermissionDenied("Sorry, this feature is only available to current STARS Participants")
        
        save = False
        if ss.status == 'r':
            if ss.pdf_report:
                return HttpResponseRedirect(ss.pdf_report.url)
            else:
                save = True
                
        pdf = ss.get_pdf(save=save)
        response = HttpResponse(pdf, mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=%s.pdf' % ss.institution.slug
        return response 

class ScorecardInternalNotesView(InstitutionAccessMixin, ScorecardView):
    """
        An extension of the scorecard view that requires permission on the selected institution.
    """
    
    # Mixin required properties
    access_level = 'observer'
    
class DataCorrectionView(CreditNavMixin, ScorecardMixin, FormActionView):
    """
        Provides a form for institutions to request a data correction
    """
    form_list = []
    template = "institutions/new_data_correction.html"
    
    def get_extra_context(self, request, *args, **kwargs):
        """ Expects arguments for category_id/subcategory_id/credit_id """
        
        _context = self.get_submissionset_context(request, **kwargs)
        
        #@todo: get submission field
        field_type = ContentType.objects.get(id=kwargs['field_type'])
        field = field_type.get_object_for_this_type(id=kwargs['field_id'])
        _context['reporting_field'] = field
        
        return _context
    
    def get_success_action(self, request, context, form):
        """
            On successful submission of the form, redirect to the returned URL
            Returns None if redirect not necessary
        """

        field = context['reporting_field']
        
        correction = form.save(commit=False)
        correction.reporting_field = field
        correction.user = request.user
        correction.save()
        
        et = EmailTemplate.objects.get(slug="data_correction_request")
        context = {
            "correction": correction,
            "submissionset": context['submissionset']
        }
        et.send_email(["stars@aashe.org",], context)

        return direct_to_template(request, "institutions/data_correction_request/success.html", context)
    
data_correction_view = DataCorrectionView("institutions/data_correction_request/new.html", DataCorrectionRequestForm)
    
class SubmissionInquirySelectView(FormActionView):
    """
        Provides a form for people to dispute the submission for a particular institution.
    """
    
    def get_success_action(self, request, context, form):
        
        if form.is_valid():
            ss = form.cleaned_data['institution']
            return HttpResponseRedirect("%sinquiry/" % ss.get_scorecard_url())
        
inquiry_select_institution = SubmissionInquirySelectView(
                                                            formClass=SubmissionSelectForm,
                                                            template='institutions/inquiries/select_submission.html',
                                                            init_context={'form_title': "STARS Submission Accuracy Inquiry",},
                                                            form_name='object_form'
                                                        )

class SubmissionInquiryView(CreditNavMixin, ScorecardMixin, MultiFormView):
    """
        Allows a visitor to submit disputes for several credits at once
    """
    
    form_list = []
    template = "institutions/inquiries/new.html"
    
    def get_context(self, request, *args, **kwargs):
        """ Expects arguments for category_id/subcategory_id/credit_id """
        
        context = self.get_submissionset_context(request, **kwargs)
        
        # add the recaptcha key
        context['recaptcha_public_key'] = settings.RECAPTCHA_PUBLIC_KEY
        
        return context
        
    def get_form_list(self, request, context):
        
        form_list, _context = super(SubmissionInquiryView, self).get_form_list(request, context)
        if not form_list:
            form_list = {}
        
        new_inquiry = SubmissionInquiry(submissionset=_context['submissionset'])
        if request.method == 'POST':
            form_list['inquirer_details'] = SubmissionInquiryForm(request.POST, instance=new_inquiry, auto_id='id_for_%s')
        else:
            form_list['inquirer_details'] = SubmissionInquiryForm(instance=new_inquiry, auto_id='id_for_%s')
        _context['inquirer_details'] = form_list['inquirer_details']
        
        # Create formset for credit inquiries
        formset = inlineformset_factory(    SubmissionInquiry, 
                                            CreditSubmissionInquiry, 
                                            can_delete=False,
                                            extra=1)
        formset.form = staticmethod(curry(CreditSubmissionInquiryForm, creditset=context['submissionset'].creditset))
        if request.method == 'POST':
            form_list['credit_inquiries'] = formset(request.POST, instance=new_inquiry)
        else:
            form_list['credit_inquiries'] = formset(instance=new_inquiry)
        _context['credit_inquiries'] = form_list['credit_inquiries']
        
        _context['recaptcha_html'] = mark_safe(captcha.displayhtml(public_key=settings.RECAPTCHA_PUBLIC_KEY))
        
        return form_list, _context
    
    def process_forms(self, request, context):
        
        form_list, _context = self.get_form_list(request, context)
        if request.method == 'POST':
            captcha_validated = True
            recaptcha_response = captcha.submit(
                                        request.POST.get('recaptcha_challenge_field', None),
                                        request.POST.get('recaptcha_response_field', None),
                                        settings.RECAPTCHA_PRIVATE_KEY,
                                        request.META['REMOTE_ADDR']
                                        )
            if not recaptcha_response.is_valid:
                context['recaptcha_error'] = recaptcha_response.error_code
                flashMessage.send("Captcha Message didn't validate.", flashMessage.ERROR)
                captcha_validated = False
            
            if not form_list['inquirer_details'].is_valid() or not form_list['credit_inquiries'].is_valid():
                flashMessage.send("Please correct the errors below.", flashMessage.ERROR)
            elif captcha_validated:
                submission_inquiry = form_list['inquirer_details'].save(commit=False)
                submission_inquiry.save()
                form_list['credit_inquiries'].save()
                
                # Send confirmation email
                email_to = [context['institution'].contact_email, submission_inquiry.email_address]
                et = EmailTemplate.objects.get(slug="submission_accuracy_inquiry")
                email_context = {
                    "inquiry": submission_inquiry,
                    "institution": submission_inquiry.submissionset.institution
                }
                et.send_email(email_to, email_context)
                            
                return context, self.get_success_response(request, context)
                
        return context, None
        
    def get_success_response(self, request, context):
        r = direct_to_template(request, "institutions/inquiries/success.html", context)
        return r
