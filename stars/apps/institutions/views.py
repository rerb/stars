from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from django.core.exceptions import PermissionDenied
from django.utils.functional import curry
from django.forms.models import inlineformset_factory
from django.template import Context, Template
from django.core.mail import send_mail
from django.template.loader import get_template

import sys, re
from datetime import date
from recaptcha.client import captcha

from stars.apps.auth.utils import respond
from stars.apps.auth.mixins import InstitutionAccessMixin
from stars.apps.credits.models import CreditSet
from stars.apps.submissions.models import *
from stars.apps.institutions.models import Institution, InstitutionState, StarsAccount
from stars.apps.institutions.forms import *
from stars.apps.helpers.forms.views import TemplateView, FormActionView, MultiFormView
from stars.apps.credits.views import CreditNavMixin

class SortableTableView(TemplateView):
    """
        A class-based view for displaying a sortable list of objects
        The extending class should set two property variables: `columns` and `default_key`
        And override the `get_queryset` method
    """
    
    columns = None # This is coupled to the template :(
    default_key = None # The default column to sort on
    
    def __init__(self, *args, **kwargs):
        
        # make sure that the extending class has defined the requred properties.
        assert (self.columns and self.default_key), "Must `colums` and `default_key` when extending this class"
        return super(SortableTableView, self).__init__(*args, **kwargs)
    
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

class ActiveInstitutions(SortableTableView):
    """
        Extending SortableTableView to show a sortable list of all active submissionsets
    """

    default_key = 'status'
    default_rev = ''
    secondary_order_field = 'institution__name'
    columns = [
                    {
                        'key': 'name',
                        'sort_field': 'institution__name',
                        'title': 'Institution',
                    },
                    {
                        'key': 'status',
                        'sort_field': 'status',
                        'title': 'Status',
                    },
                    {
                        'key': 'rating',
                        'sort_field': 'rating',
                        'title': 'Rating',
                    },
                    {
                        'key': 'date_registered',
                        'sort_field': 'date_registered',
                        'title': 'Date Registered',
                    },
                    {
                        'key':'deadline',
                        'sort_field':'submission_deadline',
                        'title':'Submission Deadline',
                    },
              ]
              
    def get_queryset(self):
        return SubmissionSet.objects.published()

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
        for ss in institution.submissionset_set.all():
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
                    
        if len(submission_sets) < 1:
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
        """
        context = {}
        # Get the Institution
        if kwargs.has_key('institution_slug'):
            institution = get_object_or_404(Institution, slug=kwargs['institution_slug'])
            context['institution'] = institution
            
            # Check that the user has a StarsAccount for this institution, or is an admin
            if request.user.is_authenticated():
                try:
                    account = StarsAccount.objects.get(institution=institution, user=request.user)
                except StarsAccount.DoesNotExist:
                    account = None
                    
                if account or request.user.has_perm('admin'):
                    context['user_tied_to_institution'] = True
                
            
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
    
    def get_context(self, request, *args, **kwargs):
        """ Expects arguments for category_id/subcategory_id/credit_id """
        
        context = self.get_submissionset_context(request, **kwargs)
        
        url_prefix = context['submissionset'].get_scorecard_url()
            
        context['outline'] = self.get_creditset_navigation(context['submissionset'].creditset, url_prefix=url_prefix, current=context['current'])
        
        context['score'] = context['submissionset'].get_STARS_score()
        context['rating'] = context['submissionset'].get_STARS_rating()
        
        return context
        
    

class ScorecardInternalNotesView(InstitutionAccessMixin, ScorecardView):
    """
        An extension of the scorecard view that requires permission on the selected institution.
    """
    
    # Mixin required properties
    access_level = 'observer'
    def raise_redirect(self):
        raise Http404
    fail_response = raise_redirect
    
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
            form_list['inquirer_details'] = SubmissionInquiryForm(request.POST, instance=new_inquiry)
        else:
            form_list['inquirer_details'] = SubmissionInquiryForm(instance=new_inquiry)
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
        
        return form_list, _context
    
    def process_forms(self, request, context):
        
        form_list, _context = self.get_form_list(request, context)
        if request.method == 'POST':
            captcha_validated = False
            recaptcha_response = captcha.submit(
                                        request.POST.get('recaptcha_challenge_field', None),
                                        request.POST.get('recaptcha_response_field', None),
                                        settings.RECAPTCHA_PRIVATE_KEY,
                                        request.META['REMOTE_ADDR']
                                        )
            if not recaptcha_response.is_valid:
                context['recaptcha_error'] = recaptcha_response.error_code
                flashMessage.send("Captcha Message didn't validate.", flashMessage.ERROR)
            else:
                captcha_validated = True
                if form_list['inquirer_details'].is_valid():
                    submission_inquiry = form_list['inquirer_details'].save(commit=False)
                    if form_list['credit_inquiries'].is_valid() and captcha_validated:
                        submission_inquiry.save()
                        form_list['credit_inquiries'].save()
                        
                        # Send confirmation email
                        email_context = Context({'inquiry': submission_inquiry,'institution': context['institution'],})
                        t = get_template("institutions/inquiries/liaison_email.txt")
                        message = t.render(email_context)
                        
                        email_to = [context['institution'].contact_email, submission_inquiry.email_address, 'stars@aashe.org',]
                        send_mail(  "STARS Submission Data Accuracy Inquiry",
                                    message,
                                    submission_inquiry.email_address,
                                    email_to,
                                    fail_silently=False
                                    )
                                    
                        return context, self.get_success_response(request, {'form_title': 'Successful Inquiry',})
                    else:
                        validated = False
                else:
                    validated = False
                if not validated:
                    flashMessage.send("Please correct the errors below.", flashMessage.ERROR)
        return context, None
        
    def get_success_response(self, request, context):
        r = direct_to_template(request, "custom_forms/form_success.html", context)
        return r