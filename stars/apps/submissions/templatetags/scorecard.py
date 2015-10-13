from logging import getLogger

from django import template


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
def subcategory_quartiles(subcategory):

    class Quartile(object):

        def __init__(self, **kwargs):
            self.absolute_one = kwargs.get('absolute_one', .0)
            self.absolute_two = kwargs.get('absolute_two', .0)
            self.absolute_three = kwargs.get('absolute_three', .0)
            self.absolute_four = kwargs.get('absolute_four', .0)
            self.absolute_one_percent = int(self.absolute_one * 100)
            self.absolute_two_percent = int(self.absolute_two * 100)
            self.absolute_three_percent = int(self.absolute_three * 100)
            self.absolute_four_percent = int(self.absolute_four * 100)
            self.relative_one = self.absolute_one
            self.relative_two = self.absolute_two - self.absolute_one
            self.relative_three = self.absolute_three - self.absolute_two
            self.relative_four = self.absolute_four - self.absolute_three

    q = Quartile(absolute_one=.15,
                 absolute_two=.3,
                 absolute_three=.6,
                 absolute_four=.8)

    return q
