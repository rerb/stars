from logging import getLogger

from django import template

from stars.apps.submissions.models import SubcategoryQuartiles


register = template.Library()


logger = getLogger('stars')


@register.simple_tag
def category_color(category_abbreviation):
    """Return the color for a category, by abbreviation.
    """
    color_map = {
        'AC': '#00bce4',
        'ER': '#00bce4',
        'EN': '#a486bd',
        'OP': '#6bbc49',
        'PA': '#cedc45',
        'PAE': '#cedc45',
        'IN': '#15387f'
    }

    return color_map[category_abbreviation]


@register.assignment_tag
def subcategory_quartiles(subcategory_submission):

    class Quartiles(object):

        def __init__(self, **kwargs):
            self.absolute_first = kwargs.get('absolute_first', .0)
            self.absolute_second = kwargs.get('absolute_second', .0)
            self.absolute_third = kwargs.get('absolute_third', .0)
            self.absolute_fourth = kwargs.get('absolute_fourth', .0)
            self.absolute_first_percent = round(self.absolute_first * 100, 2)
            self.absolute_second_percent = round(self.absolute_second * 100, 2)
            self.absolute_third_percent = round(self.absolute_third * 100, 2)
            self.absolute_fourth_percent = round(self.absolute_fourth * 100, 2)
            self.relative_first = self.absolute_first
            self.relative_second = self.absolute_second - self.absolute_first
            self.relative_third = self.absolute_third - self.absolute_second
            self.relative_fourth = self.absolute_fourth - self.absolute_third

    subcategory = subcategory_submission.subcategory
    submission_set = subcategory_submission.get_submissionset()
    org_type = submission_set.institution.org_type

    cached_quartiles = SubcategoryQuartiles.objects.get(
        subcategory=subcategory,
        org_type=org_type)

    absolute_first = cached_quartiles.first / 100
    absolute_second = cached_quartiles.second / 100
    absolute_third = cached_quartiles.third / 100
    absolute_fourth = cached_quartiles.fourth / 100

    quartiles = Quartiles(absolute_first=absolute_first,
                          absolute_second=absolute_second,
                          absolute_third=absolute_third,
                          absolute_fourth=absolute_fourth)

    return quartiles
