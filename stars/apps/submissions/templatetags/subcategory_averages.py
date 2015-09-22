from logging import getLogger

from django import template

from stars.apps.submissions.models import SubcategoryOrgTypeAveragePoints


register = template.Library()


logger = getLogger('stars')


@register.assignment_tag
def subcategory_submission_average_points(subcategory_submission):
    """Return the average_points for the subcategory and institution
    org type derieved from subcategory_submission.

    If no matching SubcategoryOrgTypeAveragePoints is found, one is
    created, and then average_points are calculated.
    """
    subcategory = subcategory_submission.subcategory
    org_type = (
        subcategory_submission.category_submission.submissionset.get_org_type(
        ))
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
