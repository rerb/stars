from django.views.generic.base import TemplateView
from django.conf import settings
from django.core.cache import cache

from stars.apps.submissions.models import SubmissionSet
from stars.apps.credits.models import Rating

from sorl.thumbnail import get_thumbnail

from datetime import date

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
            cache.set('stars_dashboard_context', _context, 60*30) # cache this for 30 minutes
        
        _context.update(super(Dashboard, self).get_context_data(**kwargs))
        return _context