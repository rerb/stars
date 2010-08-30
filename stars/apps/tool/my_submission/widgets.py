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
            filepath = url = value.url
            # why not use os.path.basename(path) to get the filename here?
            match = re.match(".*/([^/]+)$", url)
            filename = match.groups()[0] if match else filepath
            
            # render a delete button for the file that uses a JS AJAX call to perform the deletion
            element_id = '%s-current'%name
            url = "/tool/submissions/gateway%s/delete/"%filepath
            delete_button = """
                <button type='button' 
                        onclick='delete_file("%s", "%s", "%s");'>
                   delete
                </button>
            """%(element_id, filename, url)

            output.append("""
                <div id=%s> 
                   %s <a target="_blank" href="%s">%s</a> %s 
                </div> 
                %s
            """%(element_id, 'Currently:', value.url, filename, delete_button, 'Change:'))
            
        output.append(super(UploadFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))
