from django.forms import FileInput
from django.utils.safestring import mark_safe

import re

from stars.apps.helpers import watchdog

class UploadFileWidget(FileInput):
    """
    A FileField Widget that shows its current value if it has one.
    Based on django.contrib.admin.widgets.AdminFileWidget
    """
    def __init__(self, attrs={}):
        super(UploadFileWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, "url"):
            filename = url = value.url
            match = re.match(".*/([^/]+)$", url)
            if match:
                filename = match.groups()[0]
            output.append('%s <a target="_blank" href="%s">%s</a> <br />%s ' % \
                ('Currently:', value.url, filename, 'Change:'))
        output.append(super(UploadFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))