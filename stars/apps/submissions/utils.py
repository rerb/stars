from stars.apps.credits.models import Subcategory
from stars.apps.institutions.models import Institution
from stars.apps.submissions.models import SubcategoryOrgTypeAveragePoints


def load_subcategory_average_points_cache():

    org_types = Institution.get_org_types()
    subcategories = Subcategory.objects.all()
    for subcategory in subcategories:
        for org_type in org_types:
            try:
                cached_average = SubcategoryOrgTypeAveragePoints.objects.get(
                    subcategory=subcategory,
                    org_type=org_type)
            except SubcategoryOrgTypeAveragePoints.DoesNotExist:
                cached_average = SubcategoryOrgTypeAveragePoints.objects.create(
                    subcategory=subcategory,
                    org_type=org_type)
            cached_average.calculate()
