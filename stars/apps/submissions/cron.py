from stars.apps.institutions.models import *
#from stars.apps.credits.models import *
#from stars.apps.submissions.models import *

# depricated

from stars.apps.submissions.tasks import update_pie_api_cache
from stars.apps.submissions.tasks import expireRatings

update_pie_api_cache()
expireRatings()
