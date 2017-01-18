from django.template import Template, Context
from django.utils.safestring import mark_safe


def build_message(content, context):
    """
        A simple method to build a message from
        `content` - a string template
        `context` - the context to be applied to the template
    """
    # mark strings safe in context
    for k in context.keys():
        if type(context[k]) == str:
            context[k] = mark_safe(unicode(context[k]))
    t = Template(mark_safe(content))
    c = Context(context)
    return t.render(c)
