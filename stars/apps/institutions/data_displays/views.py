from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.conf import settings
from django.core.cache import cache
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect
from django.db.models import Q

from stars.apps.submissions.models import SubmissionSet
from stars.apps.institutions.models import Institution
from stars.apps.credits.models import Rating
from stars.apps.institutions.data_displays.utils import FormListWrapper
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
        
        Children must define `session_key`
    """
    
    def get_filters(self):
        return self.request.session.get(self.session_key, [])
    
    def set_filters(self, filter_dict):
        self.request.session[self.session_key] = filter_dict
        
    def add_filter(self, new_filter):
        filters = self.get_filters()
        if new_filter not in filters:
            filters.append(new_filter)
        self.set_filters(filters)
        
    def drop_filter(self, filter):
        filters = self.get_filters()
        try:
            filters.remove(filter)
            self.set_filters(filters) 
        except:
            pass
    
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
    form_class = AggregateFilterForm
    template_name = "institutions/data_displays/score.html"
    session_key = "aggregated_filter"
    success_url = "/institutions/data-displays/categories/"
    
    def get_form(self, form_class):
        """
            Provides two forms:
                1) formset for deletion of any existing filters
                2) form for adding a new filter
        """
        new_filter_form = form_class(**self.get_form_kwargs())
        
        delete_forms = {}
        for f in self.get_filters():
            kwargs = self.get_form_kwargs()
            kwargs['instance'] = f
            kwargs['prefix'] = "filter_%d" % (len(delete_forms) + 1)
            delete_forms[kwargs['prefix']] = DelAggregateFilterForm(**kwargs)
        
        form_dict = {
                        'delete_forms': FormListWrapper(delete_forms),
                        'new_filter_form': new_filter_form,
                    }
        
        form = FormListWrapper(form_dict)
        
        return form
    
    def get_context_data(self, **kwargs):
        
        _context = kwargs
        filters = self.get_filters()
        _context['filters'] = filters
        
#        q = None
        object_list = []

        for f in filters:
            
            ss_queryset = SubmissionSet.objects.filter(status='r').exclude(rating__publish_score=False)
            d = {} # {'title': <filter type:item>, "<cat>": <cat_avg>, 'total': <total_submissions>}
            d['title'] = "%s: %s" % (f['type'], f['item'])
            d['item'] = f['item']
            
            if f['key'] == "org_type":
                kwargs = {f['key']: f['item'],}
                
                org_list = Organizations.objects.filter(stars_participant_status__isnull=False).filter(**kwargs).values_list('account_num', flat=True)
                
                ss_list = ss_queryset.filter(institution__aashe_id__in=list(org_list))
            
            elif f['key'] == 'rating':
                
                ss_list = ss_queryset.filter(rating__name=f['item'])
            
            count = 0
            for ss in ss_list:
                for cat in ss.categorysubmission_set.all():
                    k_tot = "%s_tot" % cat.category.abbreviation
                    k_agr = "%s_agr" % cat.category.abbreviation
                    if d.has_key(k_tot):
                        d[k_tot] += 1
                    else:
                        d[k_tot] = 1
                    if d.has_key(k_agr):
                        d[k_agr] += cat.get_STARS_score()
                    else:
                        d[k_agr] = cat.get_STARS_score()
                count += 1
            d['total'] = count
            
            for k in d.keys():
                m = re.match("(\w+)_tot", k)
                if m:
                    cat_abr = m.groups()[0]
                    if d['%s_tot'% cat_abr] != 0: 
                        d["%s_avg" % cat_abr] = d['%s_agr'% cat_abr] / d['%s_tot'% cat_abr]
                    else:
                        d["%s_avg" % cat_abr] = None
            
            object_list.append(d)
                    
                
        _context['object_list'] = object_list
        
        return _context
    
    def form_valid(self, form):
        
        # Save the new filter in the session
        
        if self.request.POST['type'] and self.request.POST['item']:
            filter = {'type': self.request.POST['type'], 'item': self.request.POST['item']}
            
            # add a key value for the column
            for k,v in TYPE_CHOICES:
                if k == filter['type']:
                    filter['type'] = v
                    filter['key'] = k
                    self.add_filter(filter)
                    break
        
        # Delete requested filters
        for k,v in form.forms['delete_forms'].forms.items():
            key = '%s-delete' % k
            if self.request.POST.has_key(key) and self.request.POST[key]:
                self.drop_filter(v.instance)
        
        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form):
        flashMessage.send("Please correct the errors below.", flashMessage.ERROR)
        return super(AggregateFilter, self).form_invalid(form)
    