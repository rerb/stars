from logging import getLogger

from django import template

from stars.apps.submissions.models import SubcategoryOrgTypeAveragePoints


register = template.Library()


logger = getLogger('stars')


@register.assignment_tag
def subcategory_org_type_average_points(subcategory, org_type):
    """Return the average_points for the provided subcategory and org_type.

    If no matching SubcategoryOrgTypeAveragePoints is found, one is
    created, and then average_points are calculated.
    """
    try:
        subcategory_org_type_average_points = (
            SubcategoryOrgTypeAveragePoints.objects.get(
                subcategory=subcategory,
                org_type=org_type))
    except SubcategoryOrgTypeAveragePoints.DoesNotExist:
        logger.warning('no SubcategoryOrgTypeAveragePoints for subcategory '
                       '{subcategory}, org_type {org_type}'.format(
                           subcategory=subcategory,
                           org_type=org_type))
        logger.warning('creating SubcategoryOrgTypeAveragePoints for '
                       'subcategory {subcategory}, org_type {org_type}'.format(
                           subcategory=subcategory,
                           org_type=org_type))
        subcategory_org_type_average_points = (
            SubcategoryOrgTypeAveragePoints.objects.create(
                subcategory=subcategory,
                org_type=org_type))
        logger.warning('calculating SubcategoryOrgTypeAveragePoints for '
                       'subcategory {subcategory}, org_type {org_type}'.format(
                           subcategory=subcategory,
                           org_type=org_type))
        subcategory_org_type_average_points.calculate()
    return str(subcategory_org_type_average_points.average_points)
