
from stars.apps.auth.utils import respond
from stars.apps.auth.decorators import user_has_tool

def stars_home_page(request):
    """
        STARS home page - really a flatpage defined by the template, but with a few dynamic benefits.
    """
    template = "default.html"
    return respond(request, template, {})

@user_has_tool
def tool(request):
    """
        Display a dynamic tool, defined in the template based on account context stored with the user.
    """
    template = "tool/tool.html"
    return respond(request, template, {})
    
    
