from django import template

register = template.Library()


@register.inclusion_tag('tool/submissions/side-menu.html')
def show_collapsing_menu(outline):
    """
        This template tag takes a list of dicts, outline, with the following
        structure:

        [
            {
                'title': title,
                'url': url,
                'children':
                    [
                        {
                            'title': title,
                            'url': url,
                            'children':
                                [
                                    {
                                        'title': title,
                                        'url': url
                                    }
                                ]
                        }
                    ]
            }
        ]

        Menu items, at each level, can have the following properties

        Required

        title:
            - the name displayed for the link

        Optional

        url
        bookmark:
            - the bookmark on the page to scroll too... this could be in the
            url property but sometimes this is displayed differently
        attrs:
            - a dictionary attributes to apply to this item
            (applied to the <li> by default)
        children_attrs:
            - a dictionary of attributes to apply to the <ul> for children
    """
    return {'outline': outline}
