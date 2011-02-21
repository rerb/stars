from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.conf import settings
from django.core.cache import cache
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect
from django.db.models import Q

from stars.apps.submissions.models import *
from stars.apps.institutions.models import Institution
from stars.apps.credits.models import Rating, Credit, Category, Subcategory, DocumentationField
from stars.apps.institutions.data_displays.utils import FormListWrapper, mean_and_stdv
from stars.apps.institutions.data_displays.forms import *
from stars.apps.helpers import flashMessage

from aashe.issdjango.models import Organizations

from sorl.thumbnail import get_thumbnail

from datetime import date
import re

class Dashboard(TemplateView):
    """
        Display data in a visual form
    """
    template_name = "institutions/data_displays/dashboard.html"
    
    def get_context_data(self, **kwargs):
        
        _context = cache.get('stars_dashboard_context')
        
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
                '<cat_abbr>': {'title': '<cat_title>', 'ord': #, 'agr': #, 'tot': #, 'avg': #}
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
                                    bar_chart[cs.category.abbreviation]['agr'] += cs.get_STARS_score()
                                    bar_chart[cs.category.abbreviation]['tot'] += 1
                                else:
                                    bar_chart[cs.category.abbreviation] = {}
                                    bar_chart[cs.category.abbreviation]['title'] = cs.category.title
                                    bar_chart[cs.category.abbreviation]['ord'] = cs.category.ordinal
                                    bar_chart[cs.category.abbreviation]['agr'] = cs.get_STARS_score()
                                    bar_chart[cs.category.abbreviation]['tot'] = 1
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
                bar_chart_rows.append({'short': k, 'avg': v['agr'] / v['tot'], 'ord': v['ord'], 'title': v['title']})
                
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
            cache.set('stars_dashboard_context', _context, 60*120) # cache this for 2 hours
        
        _context.update(super(Dashboard, self).get_context_data(**kwargs))
        return _context
    
class FilteringMixin(object):
    """
        A mixin that will save filters (dictionaries) in the session
        
        Children must define `filter_keys`
        
        filters are stored in dictionaries
        
            {'<filter_group_key>': [filter_list], }
    """
    
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
        
        new_filter_form = form_class(**self.get_form_kwargs())
        
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
        
        if self.request.POST['type'] and self.request.POST['item']:
            filter = {'type': self.request.POST['type'], 'item': self.request.POST['item']}
            
            # add a key value for the column
            for k,v in TYPE_CHOICES:
                if k == filter['type']:
                    filter['type'] = v
                    filter['key'] = k
                    self.add_filter(filter, filter_group_key)
                    break
        
        # Delete requested filters
        for k,v in form.forms['delete_forms'].forms.items():
            key = '%s-delete' % k
            if self.request.POST.has_key(key) and self.request.POST[key]:
                self.drop_filter(v.instance, filter_group_key)
    
class AggregateFilter(FilteringMixin, FormView):
    """
        Provides a filtering tool which is stored in the session in the following way:
        
        Session
            key: "aggregated_filter"
            value: (list of filters)
                (
                    {
                        'type': <type>,
                        'item': <item>,
                        'key': <column>,
                    },
                )
    """
    form_class = CharacteristicFilterForm
    template_name = "institutions/data_displays/categories.html"
    filter_keys = ("aggregated_filter",)
    success_url = "/institutions/data-displays/categories/"
    
    def get_form(self, form_class):
        
        return self.get_filter_form('aggregated_filter', form_class)
    
    def get_context_data(self, **kwargs):
        
        _context = kwargs
        filters = self.get_filter_group('aggregated_filter')
        _context['filters'] = filters
        
#        q = None
        object_list = []

        for f in filters:
            
            ss_queryset = SubmissionSet.objects.filter(status='r').exclude(rating__publish_score=False)
            d = {} # {'title': <filter type:item>, "<cat>": <cat_avg>, "<cat>_list": [], 'total': <total_submissions>}
            d['title'] = "%s: %s" % (f['type'], f['item'])
            d['item'] = f['item']
            
            if f['key'] == "org_type":
                kwargs = {f['key']: f['item'],}
                
                org_list = Organizations.objects.filter(stars_participant_status__isnull=False).filter(**kwargs).values_list('account_num', flat=True)
                
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
                        d["%s_avg" % cat_abr], d["%s_std" % cat_abr] = mean_and_stdv(d['%s_list'% cat_abr])
                    else:
                        d["%s_avg" % cat_abr] = d["%s_std" % cat_abr] = None
            
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
    
class ScoreFilter(FilteringMixin, FormView):
    """
        Provides a filtering tool which is stored in the session in the following way:
    """
    form_class = CharacteristicFilterForm
    template_name = "institutions/data_displays/score.html"
    filter_keys = ("score_filter",)
    success_url = "/institutions/data-displays/scores/"
    
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
        
        _context = kwargs
        filters = self.get_filter_group('score_filter')
        _context['filters'] = filters
        
        org_q_list = []
        ss_q_list = []

        for f in filters:
            
            q_kwargs = {f['key']: f['item'],}
            q = Q(**q_kwargs)
            
            if f['key'] == 'rating__name':
                ss_q_list.append(q)
                
            else:
                org_q_list.append(q)
            
        ss_list = SubmissionSet.objects.none()
        org_ss_list = SubmissionSet.objects.none()
        
        if ss_q_list:
            ss_list = SubmissionSet.objects.filter(status='r').exclude(rating__publish_score=False)
            if ss_q_list:
                ss_list = ss_list.filter(*ss_q_list)
            
        if org_q_list:
            org_list = Organizations.objects.filter(stars_participant_status__isnull=False).filter(*org_q_list).values_list('account_num', flat=True)
            
            ss_queryset = SubmissionSet.objects.filter(status='r').exclude(rating__publish_score=False)
            org_ss_list = ss_queryset.filter(institution__aashe_id__in=list(org_list))
            
        columns = self.get_columns()
        
        if not columns:
            _context['object_list'] = None
            _context['columns'] = None
        else:
            queryset = ss_list | org_ss_list
            object_list = []
            for ss in queryset.order_by('institution__name'):
                row = {'ss': ss, 'cols': []}
                count = 0
                for k, col in columns.items():
                    if col != None:
                        score = "--"
                        units = ""
                        if isinstance(col, Category):
                            obj = CategorySubmission.objects.get(submissionset=ss, category=col)
                            score = obj.get_STARS_score()
                            units = "%"
                        elif isinstance(col, Subcategory):
                            obj = SubcategorySubmission.objects.get(category_submission__submissionset=ss, subcategory=col)
                            score = obj.get_claimed_points()
                        elif isinstance(col, Credit):
                            obj = CreditUserSubmission.objects.get(subcategory_submission__category_submission__submissionset=ss, credit=col)
                            score = obj.assessed_points
                            
                        row['cols'].append({'score': score, 'units': units})
                    
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

class ContentFilter(FilteringMixin, FormView):
    """
        Provides a filtering tool which is stored in the session in the following way:
    """
    form_class = CharacteristicFilterForm
    template_name = "institutions/data_displays/content.html"
    filter_keys = ("content_filter",)
    success_url = "/institutions/data-displays/content/"
    
    def get_form(self, form_class):
        
        filter_form = self.get_filter_form('content_filter', form_class)
        
        kwargs = self.get_form_kwargs()
        kwargs['initial'] = self.get_reporting_field()
        reporting_field_form = ReportingFieldSelectForm(**kwargs)
        
        form_dict = {
                        'filters': filter_form,
                        'reporting_field': reporting_field_form,
                    }
        
        return FormListWrapper(form_dict)
    
    def get_context_data(self, **kwargs):
        
        _context = kwargs
        filters = self.get_filter_group('content_filter')
        _context['filters'] = filters
        
        org_q_list = []
        ss_q_list = []

        for f in filters:
            
            q_kwargs = {f['key']: f['item'],}
            q = Q(**q_kwargs)
            
            if f['key'] == 'rating__name':
                ss_q_list.append(q)
                
            else:
                org_q_list.append(q)
            
        ss_list = SubmissionSet.objects.none()
        org_ss_list = SubmissionSet.objects.none()
        
        if ss_q_list:
            ss_list = SubmissionSet.objects.filter(status='r').exclude(rating__publish_score=False)
            if ss_q_list:
                ss_list = ss_list.filter(*ss_q_list)
            
        if org_q_list:
            org_list = Organizations.objects.filter(stars_participant_status__isnull=False).filter(*org_q_list).values_list('account_num', flat=True)
            
            ss_queryset = SubmissionSet.objects.filter(status='r').exclude(rating__publish_score=False)
            org_ss_list = ss_queryset.filter(institution__aashe_id__in=list(org_list))
            
        queryset = ss_list | org_ss_list
        
        rf = self.get_reporting_field()['reporting_field']
        
        if not rf:
            _context['object_list'] = None
            _context['reporting_field'] = None
        else:
            object_list = []
            for ss in queryset:
                
                field_class = DocumentationFieldSubmission.get_field_class(rf)
                cus_lookup = "subcategory_submission__category_submission__submissionset"
                # I have to get creditusersubmissions so i can be sure these are actual user submissions and not tests
                cus = CreditUserSubmission.objects.get(**{cus_lookup: ss, 'credit': rf.credit})
                df = field_class.objects.get(credit_submission=cus, documentation_field=rf)
                cred = CreditUserSubmission.objects.get(pk=df.credit_submission.id)
                object_list.append({'value': df.value, 'score': cred.assessed_points, 'ss': ss})
            _context['object_list'] = object_list
            _context['reporting_field'] = rf
        
        return _context
    
    def form_valid(self, form):
        
        # Save the new filter in the session
        self.save_filters(form.forms['filters'], 'content_filter')
        self.save_reporting_field(form)
        
        return HttpResponseRedirect(self.get_success_url())
    
    def save_reporting_field(self, form):
        
        field = form.forms['reporting_field'].cleaned_data
        
        self.request.session['reporting_field'] = field
        
    def get_reporting_field(self):
        
        return self.request.session.get('reporting_field', None)
    
    def form_invalid(self, form):
        flashMessage.send("Please correct the errors below.", flashMessage.ERROR)
        return super(ContentFilter, self).form_invalid(form)