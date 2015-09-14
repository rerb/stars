from logging import getLogger

from stars.apps.credits.models import Subcategory
from stars.apps.institutions.models import Institution
from stars.apps.submissions.models import SubcategoryOrgTypeAveragePoints


logger = getLogger('stars')


def load_subcategory_org_type_average_points():
    """Populate SubcategoryOrgTypeAveragePoints and calculate the averages.
    """
    org_types = Institution.get_org_types()
    subcategories = Subcategory.objects.all()
    for subcategory in subcategories:
        for org_type in org_types:
            logger.info('loading subcategory {subcategory} '
                        'for {org_type}'.format(subcategory=subcategory.title,
                                                org_type=org_type))
            try:
                average = SubcategoryOrgTypeAveragePoints.objects.get(
                    subcategory=subcategory,
                    org_type=org_type)
            except SubcategoryOrgTypeAveragePoints.DoesNotExist:
                average = SubcategoryOrgTypeAveragePoints.objects.create(
                    subcategory=subcategory,
                    org_type=org_type)
            average.calculate()
