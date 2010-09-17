from stars.apps.custom_forms.forms import *
from stars.apps.helpers.forms.views import FormActionView, MultiFormView

from django.views.generic.simple import direct_to_template
from django.core.mail import send_mail
from django.template.loader import get_template
from django.conf import settings
from django.template import Context, Template

import sys

#class SubmissionEnquiryView(MultiFormView):
#    """ A form for institutions to submit a question about the validity of a submission. """
#    
#    form_list = [
#            {'form_name': 'contact', 'form_class': FormClass, 'instance_name': 'instance', 'has_upload': False,}
#        ]

class EligibilityView(FormActionView):
    
    def get_success_action(self, request, context, form):
        
        self.save_form(form, request, context)
        
        responses = []
        for field in form:
            value = field.data
            if field.field.__class__.__name__ == "BooleanField":
                if value:
                    value = "YES"
                else:
                    value = "NO"
            responses.append({'label': field.label, 'value': value})
        
        _context = Context({'responses': responses,})
        t = get_template("custom_forms/eligibility_staff_email.txt")
        message = t.render(_context)
        
        email_to = ['stars@aashe.org',]
        send_mail(  "Eligibility Query from %s at %s" % (form.cleaned_data['name'], form.cleaned_data['institution']),
                    message,
                    form.cleaned_data['email'],
                    email_to,
                    fail_silently=False
                    )
        
        
        t = get_template("custom_forms/eligibility_query_response.txt")
        message = t.render(context)
        send_mail( "Thank You for your enquiry",
                   message,
                   settings.EMAIL_HOST_USER,
                   [form.cleaned_data['email'],],
                   fail_silently=False
                   )
        
        r = direct_to_template(request, "custom_forms/form_success.html", extra_context=self.context_dict)
        return r
    
eligibility = EligibilityView("custom_forms/eligibility.html", EligibilityForm, has_upload=False, form_name='object_form', init_context={'form_title': "Eligibility Enquiry",})

class TAAppView(FormActionView):
    
    def get_success_action(self, request, context, form):
        
        self.save_form(form, request, context)
        
        t = get_template("custom_forms/ta_app_email.txt")
        message = t.render(context)
        p = request.POST
        email_to = [request.POST['email'], 'susan.gentile@aashe.org',]
        send_mail(  "STARS Technical Advisor Application Received",
                    message,
                    settings.EMAIL_HOST_USER,
                    email_to,
                    fail_silently=False
                    )
        
        r = direct_to_template(request, "custom_forms/form_success.html", extra_context=self.context_dict)
        return r

ta_application = TAAppView("custom_forms/ta_app.html", TAApplicationForm, has_upload=True, form_name='object_form', init_context={'form_title': "Technical Advisor Application",})
