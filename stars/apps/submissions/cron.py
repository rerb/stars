from stars.apps.submissions.tasks import update_pie_api_cache
from stars.apps.submissions.tasks import expire_ratings

update_pie_api_cache()
expire_ratings()
