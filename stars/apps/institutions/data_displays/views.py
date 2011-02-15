from django.views.generic.base import TemplateView
from django.conf import settings
from django.core.files.images import ImageFile

from stars.apps.submissions.models import SubmissionSet

from sorl.thumbnail import get_thumbnail

class Dashboard(TemplateView):
    """
        Display data in a visual form
    """
    template_name = "institutions/data_displays/dashboard.html"
    
    def get_context_data(self, **kwargs):
        
        _context = super(Dashboard, self).get_context_data(**kwargs)
        
        i_list = []
        for ss in SubmissionSet.objects.published().order_by('rating__minimal_score'):
            d = {'institution': ss.institution.profile, 'rating': None, 'ss': ss}
            if ss.status == 'r':
                d['rating'] = ss.rating
            else:
                if ss.institution.charter_participant:
                    d['image_path'] = "/media/static/images/seals/STARS-Seal-CharterParticipant_70x70.png"
                else:
                    d['image_path'] = "/media/static/images/seals/STARS-Seal-Participant_70x70.png"
            i_list.append(d)
            
        _context['institution_list'] = i_list
        
        return _context