from django.views.generic.base import TemplateView, TemplateResponseMixin
from django.views.generic.edit import FormView
from django.conf import settings
from django.core.cache import cache
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from stars.apps.submissions.models import *
from stars.apps.institutions.models import Institution
from stars.apps.credits.models import Rating, Credit, Category, Subcategory, DocumentationField
from stars.apps.institutions.data_displays.utils import FormListWrapper, get_variance
from stars.apps.institutions.data_displays.forms import *
from stars.apps.helpers import flashMessage

from aashe.issdjango.models import Organizations

from sorl.thumbnail import get_thumbnail

from datetime import date, datetime
import re, sys

class Dashboard(TemplateView):
    """
        Display data in a visual form
    """
    template_name = "institutions/data_displays/dashboard.html"
    
    def get_context_data(self, **kwargs):
        
        _context = cache.get('stars_dashboard_context')
        cache_time = cache.get('stars_dashboard_context_cache_time')
        
        if not _context:
            _context = {}
            
            # map vars
            i_list = []
            ratings = {}
            for r in Rating.objects.all():
                if r.name not in ratings.keys():
                    ratings[r.name] = 0
            
            
            # bar chart vars
            bar_chart = {}
            """
                '<cat_abbr>': {'title': '<cat_title>', 'ord': #, 'list': [], 'avg': #}
            """
                    
            for ss in SubmissionSet.objects.published().all():
                d = {'institution': ss.institution.profile, 'rating': None, 'ss': ss}
                if ss.status == 'r':
                    d['rating'] = ss.rating
                    ratings[ss.rating.name] += 1
                    # bar chart vals
                    if ss.rating.publish_score:
                        for cs in ss.categorysubmission_set.all():
                            if cs.category.abbreviation != "IN":
                                if bar_chart.has_key(cs.category.abbreviation):
                                    bar_chart[cs.category.abbreviation]['list'].append(cs.get_STARS_score())
                                else:
                                    bar_chart[cs.category.abbreviation] = {}
                                    bar_chart[cs.category.abbreviation]['title'] = "%s (%s)" % (cs.category.title, cs.category.abbreviation)
                                    bar_chart[cs.category.abbreviation]['ord'] = cs.category.ordinal
                                    bar_chart[cs.category.abbreviation]['list'] = [cs.get_STARS_score()]
                else:
                    if ss.institution.charter_participant:
                        d['image_path'] = "/media/static/images/seals/STARS-Seal-CharterParticipant_70x70.png"
                    else:
                        d['image_path'] = "/media/static/images/seals/STARS-Seal-Participant_70x70.png"
                i_list.append(d)
                
            _context['institution_list'] = i_list
            _context['ratings'] = ratings
            
            bar_chart_rows = []
            for k,v in bar_chart.items():
                avg, std, min, max = get_variance(v['list'])
                var = "Standard Deviation: %.2f | Min: %.2f | Max %.2f" % (std, min, max)
                bar_chart_rows.append({'short': k, 'avg': avg, 'var': var, 'ord': v['ord'], 'title': v['title']})
                
            _context['bar_chart'] = bar_chart_rows
            
            # get participants-to-submission figures
            
            current_month = date.today()
            current_month = current_month.replace(day=1)
            
            def change_month(d, delta):
                
                if d.month + delta == 13:
                    d = d.replace(month=1)
                    d = d.replace(year=d.year + 1)
                elif d.month + delta == 0:
                    d = d.replace(month=12)
                    d = d.replace(year=d.year - 1)
                else:
                    d = d.replace(month=d.month+delta)
                    
                return d
            
            current_month = change_month(current_month, 1)
                
            p2s = []
            p_qs = SubmissionSet.objects.published()
            s_qs = SubmissionSet.objects.published().filter(status='r')
            current_participants = p_count = p_qs.count()
            current_submissions = s_count = s_qs.count()
            while p_count:
                slice = {}
                p_count = p_qs.filter(date_registered__lte=current_month).count()
                slice['p_count'] = p_count
                s_count = s_qs.filter(date_submitted__lte=current_month).count()
                slice['s_count'] = s_count
                slice['date'] = current_month
                current_month = change_month(current_month, -1)
                p2s.insert(0, slice)
    
            _context['p2s'] = p2s
            _context['current_participants'] = current_participants
            _context['current_submissions'] = current_submissions
            
            # the bar chart for
#                STARS Participants
#                AASHE Members
#                PCC Signatories
#                Pilot Participants
            
            member_numbers = {'members': 0, 'pcc': 0, 'pilot': 0, 'canadian': 0, 'us': 0, 'all': 0}
            for i in Institution.objects.all():
                org = i.profile
                if org.is_member:
                    member_numbers['members'] += 1
                if org.is_signatory:
                    member_numbers['pcc'] += 1
                if org.country == "Canada":
                    member_numbers['canadian'] += 1
                elif org.country == "United States of America":
                    member_numbers['us'] += 1
                else:
                    print >> sys.stderr, "No country found for %s" % org.org_name
                member_numbers['all'] += 1
            _context['member_numbers'] = member_numbers
            
            cache_time = datetime.now()
            cache.set('stars_dashboard_context', _context, 60*120) # cache this for 2 hours
            cache.set('stars_dashboard_context_cache_time', cache_time, 60*120)
        
        _context['cache_time'] = cache_time
        _context.update(super(Dashboard, self).get_context_data(**kwargs))
        return _context
    
class Filter(object):
    """
        Filters need to be a managed more programatically
        added and removed from the general list where avaialable
    """
    def __init__(self, key, title, item_list):
        self.key = key
        self.title = title
        self.item_list = item_list
    
class FilteringMixin(object):
    """
        A mixin that will save filters (dictionaries) in the session
        
        Children must define
            `filter_keys` - a key for storing filters associated with this view
            
        Optionally `available_filters` can be overridden to set the default filters
    """
    
    def get_available_filters(self):
        """
            Used to poplulate the child select using JavaScript
        """
        available_filters = [
                                Filter(
                                        'org_type',
                                        'Organization Type',
                                        [
                                            'All Institutions',
                                            'Two Year Institution',
                                            'Four Year Institution',
                                            'Graduate Institution',
                                            'System Office'
                                        ]
                                       ),
                                Filter(
                                        'rating__name',
                                        'STARS Rating',
                                        [
                                            'Bronze',
                                            'Silver',
                                            'Gold',
                                            'Platinum'
                                        ]
                                       )
                              ]
        return available_filters
    
    def get_context_data(self, **kwargs):
        
        _context = {}
        _context['available_filters'] = self.get_available_filters()
        _context.update(super(FilteringMixin, self).get_context_data(**kwargs))
        return _context
    
    def get_filters(self):
        filters = {}
        for key in self.filter_keys:
            filters[key] = self.request.session.get(key, [])
        return filters
    
    def get_filter_group(self, filter_group_key):
        return self.request.session.get(filter_group_key, [])
    
    def set_filters(self, filter_list, filter_group_key):
        self.request.session[filter_group_key] = filter_list
        
    def add_filter(self, new_filter, filter_group_key):
        filters = self.get_filter_group(filter_group_key)
        if new_filter not in filters:
            filters.append(new_filter)
        self.set_filters(filters, filter_group_key)
        
    def drop_filter(self, filter, filter_group_key):
        filters = self.get_filter_group(filter_group_key)
        try:
            filters.remove(filter)
            self.set_filters(filters, filter_group_key) 
        except:
            pass
        
    def get_filter_form(self, filter_group_key, form_class):
        """
            Provides two forms:
                1) formset for deletion of any existing filters
                2) form for adding a new filter
        """
        new_filter_form = None
        available_filters = self.get_available_filters()
        if available_filters:
            new_filter_form = form_class(available_filters, **self.get_form_kwargs())
        
        delete_forms = {}
        for f in self.get_filter_group(filter_group_key):
            kwargs = self.get_form_kwargs()
            kwargs['instance'] = f
            kwargs['prefix'] = "filter_%d" % (len(delete_forms) + 1)
            delete_forms[kwargs['prefix']] = DelCharacteristicFilterForm(**kwargs)
        
        form_dict = {
                        'delete_forms': FormListWrapper(delete_forms),
                        'new_filter_form': new_filter_form,
                    }
        
        form = FormListWrapper(form_dict)
        
        return form
        
    def save_filters(self, form, filter_group_key):
        
        if self.request.POST.has_key('type') and self.request.POST.has_key('item'):
            filter = {'type': self.request.POST['type'], 'item': self.request.POST['item']}
            
            # add a key value for the column
            for f in self.get_available_filters():
                if f.key == filter['type']:
                    filter['type'] = f.title
                    filter['key'] = f.key
                    self.add_filter(filter, filter_group_key)
                    break
        
        # Delete requested filters
        for k,v in form.forms['delete_forms'].forms.items():
            key = '%s-delete' % k
            if self.request.POST.has_key(key) and self.request.POST[key]:
                self.drop_filter(v.instance, filter_group_key)
                
    def get_filtered_queryset(self, filters):
        
        org_ss_list = []
        rating_ss_list = []

        for f in filters:
            
            filter_kwargs = {f['key']: f['item'],}
            
            ss_queryset = SubmissionSet.objects.filter(status='r')
            
            if f['key'] == 'rating__name':
                rating_ss_list = ss_queryset.filter(**filter_kwargs)
                
            else:
                org_list = Organizations.objects.filter(stars_participant_status__isnull=False).values_list('account_num', flat=True)
                if f['item'] != "All Institutions": # if the item is blank then don't use this filter
                    org_list = org_list.filter(**filter_kwargs)
                    
                org_ss_list = ss_queryset.filter(institution__aashe_id__in=list(org_list))
        
        # combine these two if they both exist
        if rating_ss_list and org_ss_list:
            queryset = rating_ss_list.filter(id__in=org_ss_list)
        elif rating_ss_list and not org_ss_list:
            queryset = rating_ss_list
        elif org_ss_list and not rating_ss_list:
            queryset = org_ss_list
        else:
            queryset = SubmissionSet.objects.none()
            
        return queryset
    
class NarrowFilteringMixin(FilteringMixin):
    """
        Removes a filter once it's in use
    """
    def get_available_filters(self):
        available_filters = super(NarrowFilteringMixin, self).get_available_filters()
        for f in self.get_filter_group(self.filter_keys[0]):
            for af in available_filters:
                if af.key == f['key']:
                    available_filters.remove(af)
        return available_filters
    
class DisplayAccessMixin(object):
    """
        Objects must define two properties:
        
            denied_template_name = ""
            access_list = ['', ''] valid strings are 'member' and 'participant'
            
        if either access level is fulfilled then they pass
        if access_list is empty no access levels are required
        
        users must be authenticated
    """
    def deny_action(self, request):
        """
            @todo - I should turn this into some sort of (class?) decorator
        """
        
        if self.access_list:
            denied = True
            if 'member' in self.access_list:
                if request.user.get_profile().is_member:
                    denied = False
            if 'participant' in self.access_list:
                if request.user.get_profile().is_participant():
                    denied = False
            if denied:
                self.template_name = self.denied_template_name
                return self.render_to_response({})
        return None
    
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        
        deny_action = self.deny_action(request)
        if deny_action:
            return deny_action
        
        return super(DisplayAccessMixin, self).get(request, *args, **kwargs)
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        
        deny_action = self.deny_action(request)
        if deny_action:
            return deny_action
        
        return super(DisplayAccessMixin, self).post(request, *args, **kwargs)
    
    
class AggregateFilter(DisplayAccessMixin, FilteringMixin, FormView):
    """
        Provides a filtering tool for average category scores
        
        Participants and Members Only
    """
    form_class = CharacteristicFilterForm
    template_name = "institutions/data_displays/categories.html"
    filter_keys = ("aggregated_filter",)
    success_url = "/institutions/data-displays/categories/"
    denied_template_name = "institutions/data_displays/denied_categories.html"
    access_list = ['member', 'participant']
    
    def get_form(self, form_class):
        
        return self.get_filter_form('aggregated_filter', form_class)
    
    def get_context_data(self, **kwargs):
        
        _context = super(AggregateFilter, self).get_context_data(**kwargs)
        filters = self.get_filter_group('aggregated_filter')
        _context['filters'] = filters
        
#        q = None
        object_list = []

        for f in filters:
            
            ss_queryset = SubmissionSet.objects.filter(status='r').exclude(rating__publish_score=False)
            d = {} # {'title': <filter type:item>, "<cat>": <cat_avg>, "<cat>_list": [], 'total': <total_submissions>}
            if f['key'] == "rating__name":
                d['title'] = "%s Rated Institutions" % f['item']
            else:
                d['title'] = f['item']
            d['item'] = f['item']
            
            if f['key'] == "org_type":
                
                if f['item'] != "All Institutions":
                    kwargs = {f['key']: f['item'],}
                    org_list = Organizations.objects.filter(stars_participant_status__isnull=False).filter(**kwargs).values_list('account_num', flat=True)
                else:
                    org_list = Organizations.objects.filter(stars_participant_status__isnull=False).values_list('account_num', flat=True)
                
                ss_list = ss_queryset.filter(institution__aashe_id__in=list(org_list))
            
            elif f['key'] == 'rating__name':
                
                ss_list = ss_queryset.filter(rating__name=f['item'])
            
            count = 0
            for ss in ss_list:
                for cat in ss.categorysubmission_set.all():
                    k_list = "%s_list" % cat.category.abbreviation
                    if not d.has_key(k_list):
                        d[k_list] = []
                    d[k_list].append(cat.get_STARS_score())
                count += 1
            d['total'] = count
            
            for k in d.keys():
                m = re.match("(\w+)_list", k)
                if m:
                    cat_abr = m.groups()[0]
                    if len(d['%s_list'% cat_abr]) != 0: 
                        d["%s_avg" % cat_abr], std, min, max = get_variance(d['%s_list'% cat_abr])
                    else:
                        d["%s_avg" % cat_abr] = std, min, max = None
                    d['%s_var' % cat_abr] = "Standard Deviation: %.2f | Min: %.2f | Max %.2f" % (std, min, max)
            
            object_list.insert(0, d)
                    
        _context['object_list'] = object_list
        
        return _context
    
    def form_valid(self, form):
        
        # Save the new filter in the session
        self.save_filters(form, 'aggregated_filter')
        
        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form):
        flashMessage.send("Please correct the errors below.", flashMessage.ERROR)
        return super(AggregateFilter, self).form_invalid(form)
    
class ScoreFilter(DisplayAccessMixin, NarrowFilteringMixin, FormView):
    """
        Provides a filtering tool for scores
        
        Participants Only
    """
    form_class = CharacteristicFilterForm
    template_name = "institutions/data_displays/score.html"
    filter_keys = ("score_filter",)
    success_url = "/institutions/data-displays/scores/"
    denied_template_name = "institutions/data_displays/denied_score.html"
    access_list = ['participant']
    
    def get_form(self, form_class):
        
        filter_form = self.get_filter_form('score_filter', form_class)
        
        kwargs = self.get_form_kwargs()
        kwargs['initial'] = self.get_columns()
        col_form = ScoreColumnForm(**kwargs)
        
        form_dict = {
                        'filters': filter_form,
                        'columns': col_form,
                    }
        
        return FormListWrapper(form_dict)
    
    def get_context_data(self, **kwargs):
        
        _context = super(ScoreFilter, self).get_context_data(**kwargs)
        filters = self.get_filter_group('score_filter')
        _context['filters'] = filters
        
        cols = self.get_columns()
        
        if not cols:
            _context['object_list'] = None
            _context['columns'] = None
        else:
            
            columns = []
            for k, col in cols.items():
                columns.insert(0, (k, col))
                
            queryset = self.get_filtered_queryset(filters)
            object_list = []
            for ss in queryset.order_by('institution__name').exclude(rating__publish_score=False):
                row = {'ss': ss, 'cols': []}
                count = 0
                for k, col in columns:
                    if col != None:
                        score = "--"
                        units = ""
                        if isinstance(col, Category):
                            obj = CategorySubmission.objects.get(submissionset=ss, category=col)
                            score = "%.2f" % obj.get_STARS_score()
                            if obj.category.abbreviation != "IN":
                                units = "%"
                            url = obj.get_scorecard_url()
                        elif isinstance(col, Subcategory):
                            obj = SubcategorySubmission.objects.get(category_submission__submissionset=ss, subcategory=col)
                            score = "%.2f / %.2f" % (obj.get_claimed_points(), obj.get_adjusted_available_points())
                            url = obj.get_scorecard_url()
                        elif isinstance(col, Credit):
                            cred = CreditUserSubmission.objects.get(subcategory_submission__category_submission__submissionset=ss, credit=col)
                            url = cred.get_scorecard_url()
                            if ss.rating.publish_score:
                                if cred.submission_status == "na":
                                    score = "Not Applicable"
                                elif cred.submission_status == 'np' or cred.submission_status == 'ns':
                                    score = "Not Pursuing"
                                else:
                                    if cred.credit.type == "t1":
                                        score = "%.2f / %d" % (cred.assessed_points, cred.credit.point_value)
                                    else:
                                        score = "%.2f / %.2f" % (cred.assessed_points, ss.creditset.tier_2_points)
                            else:
                                score = "Reporter"
                            
                        row['cols'].append({'score': score, 'units': units, 'url': url})
                    
                object_list.append(row)
                    
            _context['object_list'] = object_list
            _context['columns'] = columns
        
        return _context
    
    def form_valid(self, form):
        
        # Save the new filter in the session
        self.save_filters(form.forms['filters'], 'score_filter')
        self.save_columns(form)
        
        return HttpResponseRedirect(self.get_success_url())
    
    def save_columns(self, form):
        
        columns = form.forms['columns'].cleaned_data
        
        self.request.session['columns'] = columns
        
    def get_columns(self):
        
        return self.request.session.get('columns', None)
    
    def form_invalid(self, form):
        flashMessage.send("Please correct the errors below.", flashMessage.ERROR)
        return super(ScoreFilter, self).form_invalid(form)

class ContentFilter(DisplayAccessMixin, NarrowFilteringMixin, FormView):
    """
        Provides a filtering tool for scores
        
        Participants and Members Only
    """
    form_class = CharacteristicFilterForm
    template_name = "institutions/data_displays/content.html"
    filter_keys = ("content_filter",)
    success_url = "/institutions/data-displays/content/"
    denied_template_name = "institutions/data_displays/denied_content.html"
    access_list = ['member', 'participant']
    
    def get_form(self, form_class):
        
        filter_form = self.get_filter_form('content_filter', form_class)
        
        kwargs = self.get_form_kwargs()
        kwargs['initial'] = {'reporting_field': self.get_reporting_field()}
        reporting_field_form = ReportingFieldSelectForm(**kwargs)
        
        form_dict = {
                        'filters': filter_form,
                        'reporting_field': reporting_field_form,
                    }
        
        return FormListWrapper(form_dict)
    
    def get_context_data(self, **kwargs):
        
        _context = super(ContentFilter, self).get_context_data(**kwargs)
        filters = self.get_filter_group('content_filter')
        _context['filters'] = filters
        _context['google_api_key'] = settings.GOOGLE_API_KEY
        
        
        rf = self.get_reporting_field()
            
        if not rf:
            _context['object_list'] = None
            _context['reporting_field'] = None
        else:
            queryset = self.get_filtered_queryset(filters)
            object_list = []
            for ss in queryset.order_by('institution__name'):
                
                field_class = DocumentationFieldSubmission.get_field_class(rf)
                cus_lookup = "subcategory_submission__category_submission__submissionset"
                # I have to get creditusersubmissions so i can be sure these are actual user submissions and not tests
                cus = CreditUserSubmission.objects.get(**{cus_lookup: ss, 'credit': rf.credit})
                try:
                    df = field_class.objects.get(credit_submission=cus, documentation_field=rf)
                    cred = CreditUserSubmission.objects.get(pk=df.credit_submission.id)
                    row = {'field': df, 'ss': ss, 'credit': cred}
                    if ss.rating.publish_score:
                        if cred.submission_status == "na":
                            row['score'] = "Not Applicable"
                        elif cred.submission_status == 'np' or cred.submission_status == 'ns':
                            row['score'] = "Not Pursuing"
                        else:
                            row['score'] = "%.2f / %d" % (cred.assessed_points, cred.credit.point_value)
                    else:
                        row['score'] = "Reporter"
                
                except:
                    row = {'field': None, 'ss': ss, 'credit': None, "score": None}
                object_list.append(row)
            _context['object_list'] = object_list
            _context['reporting_field'] = rf
        
        return _context
    
    def form_valid(self, form):
        
        # Save the new filter in the session
        self.save_filters(form.forms['filters'], 'content_filter')
        self.save_reporting_field(form)
        
        return HttpResponseRedirect(self.get_success_url())
    
    def save_reporting_field(self, form):
        
        field = form.forms['reporting_field'].cleaned_data['reporting_field']
        
        self.request.session['reporting_field'] = field
        
    def get_reporting_field(self):
        
        return self.request.session.get('reporting_field', None)
    
    def form_invalid(self, form):
        flashMessage.send("Please correct the errors below.", flashMessage.ERROR)
        return super(ContentFilter, self).form_invalid(form)
    
class CallbackView(TemplateView):
    """
        Child classes must implement self.get_object_list()
    """
    
    template_name = "institutions/data_displays/option_callback.html"
    
    def get_context_data(self, **kwargs):
        
        _context = super(CallbackView, self).get_context_data(**kwargs)
        if self.request.GET.has_key('current'):
            _context['current'] = int(self.request.GET['current'])
        
        _context['object_list'] = self.get_object_list(**kwargs)
        
        return _context
    
class CategoryInCreditSetCallback(CallbackView):
    """
        A callback method that accepts returns a list of
        categories as <options> for a <select>
    """
    def get_object_list(self, **kwargs):
        
        cs = CreditSet.objects.get(pk=kwargs['cs_id'])
        return cs.category_set.all()
    

class SubcategoryInCategoryCallback(CallbackView):
    """
        A callback method that accepts returns a list of
        subcategories as <options> for a <select>
    """
    def get_object_list(self, **kwargs):
        
        cat = Category.objects.get(pk=kwargs['category_id'])
        return cat.subcategory_set.all()

class CreditInSubcategoryCallback(CallbackView):
    """
        A callback method that accepts returns a list of
        credits as <options> for a <select>
    """
    def get_object_list(self, **kwargs):
        
        sub = Subcategory.objects.get(pk=kwargs['subcategory_id'])
        return sub.credit_set.all()

class FieldInCreditCallback(CallbackView):
    """
        A callback method that accepts returns a list of
        documentation fields as <options> for a <select>
    """
    def get_object_list(self, **kwargs):
        
        credit = Credit.objects.get(pk=kwargs['credit_id'])
        return credit.documentationfield_set.all()
