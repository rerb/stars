from stars.apps.custom_forms.forms import TAApplicationForm
from stars.apps.helpers.forms.views import FormActionView

from django.views.generic.simple import direct_to_template
from django.core.mail import send_mail
from django.template.loader import get_template
from django.conf import settings

class TAAppView(FormActionView):
    def get_success_response(self, request):
        
        t = get_template("custom_forms/ta_app_email.txt")
        message = t.render(self.context_dict)
        p = request.POST
        email_to = [request.POST['email'],]
        send_mail(  "STARS Technical Advisor Application Received",
                    message,
                    settings.EMAIL_HOST_USER,
                    email_to,
                    fail_silently=False
                    )
        
        r = direct_to_template(request, "custom_forms/form_success.html", extra_context=self.context_dict)
        return r

ta_application = TAAppView("custom_forms/ta_app.html", TAApplicationForm, has_upload=True, form_name='object_form', init_context={'form_title': "Technical Advisor Application",})