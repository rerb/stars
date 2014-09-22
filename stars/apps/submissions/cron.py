from stars.apps.institutions.models import *
#from stars.apps.credits.models import *
#from stars.apps.submissions.models import *

from tasks import update_pie_api_cache
from tasks import expireRatings

update_pie_api_cache()
expireRatings()
