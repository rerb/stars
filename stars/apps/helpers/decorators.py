from django.utils.safestring import mark_safe
"""
    General-purpose decorators used to wrap functions to extend their capabilities
"""

def render_with_units(render, units):
    """
        Wraps the render function to add units - useful for adding units to a widget's render method
        Usage:  widget.render = render_with_units(widget.render, units)
    """
    def wrap(*args, **kwargs):
        return mark_safe("%s <label class='units'>%s</label>"%(render(*args, **kwargs), units)) if units else render(*args, **kwargs)
    wrap.__doc__=render.__doc__
    wrap.__name__=render.__name__
    return wrap
