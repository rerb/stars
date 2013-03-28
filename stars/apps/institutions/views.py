from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.views.generic.simple import direct_to_template
from django.views.generic import FormView, CreateView, TemplateView

from extra_views import CreateWithInlinesView

from stars.apps.submissions.models import (SubmissionInquiry,
                                           DataCorrectionRequest)
from stars.apps.submissions.rules import user_can_preview_submission
from stars.apps.submissions.views import SubmissionStructureMixin
from stars.apps.institutions.models import Institution
from stars.apps.institutions.forms import (SubmissionSelectForm,
                                           SubmissionInquiryForm,
                                           CreditSubmissionInquiryFormSet,
                                           DataCorrectionRequestForm)
from stars.apps.notifications.models import EmailTemplate
from stars.apps.credits.views import StructureMixin

from aashe_rules.mixins import RulesMixin


class InstitutionStructureMixin(StructureMixin):
    """
        Extends the StructureMixin to work with Institutions
    """
    def __init__(self, *args, **kwargs):
        super(InstitutionStructureMixin, self).__init__(*args, **kwargs)

    def update_context_callbacks(self):
        super(InstitutionStructureMixin, self).update_context_callbacks()
        self.add_context_callback("get_institution")

    def get_institution(self, use_cache=True):
        """
            Attempts to get an institution.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        return self.get_obj_or_call(
                                    cache_key='institution',
                                    kwargs_key='institution_slug',
                                    klass=Institution,
                                    property="slug",
                                    use_cache=use_cache
                                    )


class SortableTableView(TemplateView):
    """
        A class-based view for displaying a sortable list of objects
        The extending class should set two property variables:
            `columns` and `default_key`
        And override the `get_queryset` method
    """

    columns = None  # This is coupled to the template :(
    default_key = None  # The default column to sort on

    def __init__(self, *args, **kwargs):

        # make sure that the extending class has defined the required properties.
        assert (self.columns and self.default_key), "Must set `colums` and `default_key` when extending this class"
        return super(SortableTableView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """ Add/update any context variables """
        _context = super(SortableTableView, self).get_context_data(**kwargs)

        _context.update({'sort_columns': self.columns, 'default_key': self.default_key})

        (_context['sort_key'], _context['rev'], _context['object_list']) = self.get_object_list()

        return _context

    def get_queryset(self):
        """ Gets the base queryset for the object_list """
        raise NotImplementedError, "Please override this method"

    def get_object_list(self):
        """
            Returns a queryset based on the GET Parameters
            Also returns the selected `sort_key`
            and `rev`, a "-" or empty string indicating the reverse sort order
        """

        sort_key = None
        asc = ""
        rev = ""
        queryset = self.get_queryset()

        if 'sort' in self.request.GET:
            if self.request.GET['sort'][0] == '-':
                asc = '-'
                rev = ''
                sort_key = self.request.GET['sort'][1:]
            else:
                asc = ''
                rev = '-'
                sort_key = self.request.GET['sort']
        else:
            sort_key = self.default_key
            rev = self.default_rev
            if rev == '':
                asc = '-'

        for col in self.columns:
            if col['key'] == sort_key:
                queryset = queryset.order_by("%s%s" %
                                             (asc, col['sort_field']),
                                             self.secondary_order_field)
                break

        return (sort_key, rev, queryset)


class SortableTableViewWithInstProps(SortableTableView):
    """
        Extends SortableTableView to include institutional
        properties from the list
    """

    def get_context_data(self, **kwargs):
        """
            update the context with the # of members and charter participants
        """

        _context = super(SortableTableViewWithInstProps, self).get_context_data(**kwargs)

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
        Extending SortableTableView to show a sortable list
        of all active participants
    """

    template_name = "institutions/institution_list_active.html"
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
                        'title': 'Current Rating',
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
        Extending SortableTableView to show a sortable list
        of all active submissionsets
    """

    template_name = "institutions/institution_list_rated.html"
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
                        'sort_field': 'current_rating',
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


class InstitutionScorecards(InstitutionStructureMixin, TemplateView):
    """
    Provides a list of available reports for an institution.

    Reports with is_visible == False are filtered from the list.

    Unrated SubmissionSets will be displayed to participating users only.

    If there's only one SubmissionSet to show, we short-circuit to the
    scorecard for that SubmissionSet, rather than show, and have the user
    select from, a list of one element.
    """
    template_name = 'institutions/scorecards/list.html'

    def get_context_data(self, **kwargs):
        _context = super(InstitutionScorecards, self).get_context_data(**kwargs)

        institution = self.get_institution()

        submission_sets = []
        qs = institution.submissionset_set.filter(is_visible=True)

        if not institution.is_participant:
            # non participants only see rated submissions
            qs = qs.filter(status='r')

        for ss in qs:
            if (ss.status == 'r' or
                user_can_preview_submission(self.request.user, ss)):
                submission_sets.append(ss)

        if len(submission_sets) < 1 and not institution.is_participant:
            raise Http404

        _context.update({'submission_sets': submission_sets,
                         'institution': institution})
        return _context

    def render_to_response(self, context, **response_kwargs):
        """
        If there's only one submission set to show, just jump
        to its scorecard rather than show a list with it as
        the only item in it.
        """
        if len(context['submission_sets']) is 1:
            return HttpResponseRedirect(
                context['submission_sets'][0].get_scorecard_url())
        else:
            return super(InstitutionScorecards, self).render_to_response(
                context, **response_kwargs)


class ScorecardView(RulesMixin,
                    InstitutionStructureMixin,
                    SubmissionStructureMixin,
                    TemplateView):
    """
        Browse credits according to submission in the credit browsing view
    """

    def update_logical_rules(self):

        super(ScorecardView, self).update_logical_rules()
        self.add_logical_rule({
                    'name': 'user_can_view_submission',
                    'param_callbacks':
                        [
                            ('user', "get_request_user"),
                            ('submission', "get_submissionset")
                        ],
                })

    def get_context_data(self, **kwargs):
        """ Expects arguments for category_id/subcategory_id/credit_id """
        _context = super(ScorecardView, self).get_context_data(**kwargs)

        ss = self.get_submissionset()

        url_prefix = ss.get_scorecard_url()

        _context['outline'] = self.get_creditset_nav(url_prefix=url_prefix)

        _context['score'] = ss.get_STARS_score()

        rating = ss.get_STARS_rating()
        _context['rating'] = rating

        _context['preview'] = False
        if not ss.status == 'r':
            _context['preview'] = True

        return _context

    def get_category_url(self, category, url_prefix):
        """ The default link for a category. """
        return "%s%s" % (url_prefix, category.get_browse_url())

    def get_subcategory_url(self, subcategory, url_prefix):
        """ The default link for a category. """
        return "%s%s" % (url_prefix, subcategory.get_browse_url())

    def get_credit_url(self, credit, url_prefix):
        """ The default credit link. """
        return "%s%s" % (url_prefix, credit.get_browse_url())


class ScorecardSummary(ScorecardView):
    template_name = 'institutions/scorecards/summary.html'


class ScorecardCredit(ScorecardView):
    template_name = 'institutions/scorecards/credit.html'


class ScorecardCreditDocumentation(ScorecardView):
    template_name = 'institutions/scorecards/credit_documentation.html'


class PDFExportView(RulesMixin,
                    InstitutionStructureMixin,
                    SubmissionStructureMixin,
                    TemplateView):
    """
        Displays an exported PDF version of the selected report.

        Based on a TemplateView, though there is no template, because
        TemplateView provides a get() method that View alone does not,
        as well as passing the results of all get_context_data()
        methods in the MRO as an argument to render_to_response().
    """
    def update_logical_rules(self):

        super(PDFExportView, self).update_logical_rules()
        self.add_logical_rule({
                    'name': 'user_can_view_pdf',
                    'param_callbacks':
                        [
                            ('user', "get_request_user"),
                            ('submission', "get_submissionset")
                        ],
                })

    def render_to_response(self, context, **response_kwargs):
        """ Renders the pdf as a response """

        ss = self.get_submissionset()

        save = False
        if ss.status == 'r':
            if ss.pdf_report:
                return HttpResponseRedirect(ss.pdf_report.url)
            else:
                save = True

        pdf = ss.get_pdf(save=save)
        response = HttpResponse(pdf, mimetype='application/pdf')
        response['Content-Disposition'] = ('attachment; filename=%s' %
                                           ss.get_pdf_filename())
        return response


class ScorecardInternalNotesView(ScorecardView):
    """
        An extension of the scorecard view that requires permission
        on the selected institution.
    """

    def update_logical_rules(self):

        super(ScorecardInternalNotesView, self).update_logical_rules()
        self.add_logical_rule({
                    'name': 'user_has_view_access',
                    'param_callbacks':
                        [
                            ('user', "get_request_user"),
                            ('submission', "get_institution")
                        ],
                })

    template_name = 'institutions/scorecards/internal_notes.html'


class DataCorrectionView(RulesMixin,
                         InstitutionStructureMixin,
                         SubmissionStructureMixin,
                         CreateView):
    """
        Provides a form for institutions to request a data correction
    """
    template_name = "institutions/data_correction_request/new.html"
    form_class = DataCorrectionRequestForm

    def update_logical_rules(self):
        super(DataCorrectionView, self).update_logical_rules()
        self.add_logical_rule({
                    'name': 'user_is_institution_admin',
                    'param_callbacks':
                        [
                            ('user', "get_request_user"),
                            ('submission', "get_institution")
                        ],
                })

    def form_valid(self, form):
        self.object = form.save()

        et = EmailTemplate.objects.get(slug="data_correction_request")
        context = {
            "correction": self.object,
            "submissionset": self.get_submissionset()
        }
        et.send_email(["stars@aashe.org"], context)

        _context = self.get_context_data()
        _context.update(context)

        return direct_to_template(self.request,
                                  "institutions/data_correction_request/success.html",
                                  _context)

    def get_form_kwargs(self):
        kwargs = super(DataCorrectionView, self).get_form_kwargs()
        kwargs['instance'] = DataCorrectionRequest(user=self.request.user,
                                                   reporting_field=self.get_fieldsubmission())
        return kwargs


class SubmissionInquirySelectView(FormView):
    """
        Provides a form for people to dispute the submission
        for a particular institution.
    """

    template_name = "institutions/inquiries/select_submission.html"
    form_class = SubmissionSelectForm

    def form_valid(self, form):
        ss = form.cleaned_data['institution']
        return HttpResponseRedirect("%sinquiry/" % ss.get_scorecard_url())


class SubmissionInquiryView(InstitutionStructureMixin,
                            SubmissionStructureMixin,
                            CreateWithInlinesView):
    """
        Allows a visitor to submit disputes for several credits at once
    """
    model = SubmissionInquiry
    form_class = SubmissionInquiryForm
    inlines = [CreditSubmissionInquiryFormSet]
    template_name = "institutions/inquiries/new.html"

    def get_context_data(self, **kwargs):
        _c = super(SubmissionInquiryView, self).get_context_data(**kwargs)
        return _c

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(SubmissionInquiryView, self).get_form_kwargs()
        ss = self.get_submissionset()
        kwargs.update({'instance': SubmissionInquiry(submissionset=ss)})
        return kwargs

    def forms_valid(self, form, inlines):
        """
        If the form and formsets are valid, save the associated models.
        """
        _context = self.get_context_data()
        self.object = form.save()
        for formset in inlines:
            formset.save()

#        Send confirmation email
        email_to = [_context['institution'].contact_email]
        if not self.object.anonymous and self.object.email_address:
            email_to.append(self.object.email_address)

        et = EmailTemplate.objects.get(
            slug="submission_accuracy_inquiry")
        email_context = {
            "inquiry": self.object,
            "institution": self.object.submissionset.institution
        }
        et.send_email(email_to, email_context)

        return direct_to_template(self.request,
                                  "institutions/inquiries/success.html",
                                  extra_context=_context)
