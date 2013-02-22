from django.shortcuts import render
from django.views.generic.edit import FormView

from stars.apps.custom_forms.forms import (EligibilityForm,
                                           SteeringCommitteeNominationForm,
                                           TAApplicationForm,
                                           DataDisplayAccessRequestForm)
from stars.apps.helpers.mixins import ValidationMessageFormMixin
from stars.apps.notifications.models import EmailTemplate


class BaseCustomFormView(ValidationMessageFormMixin, FormView):
    """
        Base view for custom forms

        define:
            form_class
            template_name
            success_template_name
            email_template_slug
            form_title
            block_content_slug
    """
    success_template_name = "custom_forms/form_success.html"
    template_name = 'custom_forms/form.html'

    def form_valid(self, form):
        form.save()
        self.send_confirmation_email(form)
        return render(request=self.request,
                      template_name=self.success_template_name,
                      dictionary=self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(BaseCustomFormView,
                        self).get_context_data(**kwargs)
        context['form_title'] = self.form_title
        if self.block_content_slug:
            context['block_content_slug'] = self.block_content_slug
        return context

    def send_confirmation_email(self, form):
        et = EmailTemplate.objects.get(slug=self.email_template_slug)
        et.send_email([self.request.POST['email']], self.initial)


class EligibilityView(BaseCustomFormView):
    """
        View for the form that lets folks petition for STARS membership for
        an institution that doesn't qualify under the usual conditions.
    """

    form_class = EligibilityForm
    form_title = 'Eligibility Inquiry'
    block_content_slug = "elig_form_top"

    def send_confirmation_email(self, form):
        form.send_email()


class SteeringCommitteeNominationView(BaseCustomFormView):
    """
       View for the form that lest folks apply to be sit on the STARS
       steering committee.
    """

    form_class = SteeringCommitteeNominationForm
    email_template_slug = "sc_application"
    form_title = 'STARS Steering Committee Nomination'
    block_content_slug = "sc_app"


class TechnicalAdvisorApplicationView(BaseCustomFormView):
    """
        View for the form that allows folks to apply to be STARS
        Technical Advisors.
    """
    form_class = TAApplicationForm
    email_template_slug = "ta_application"
    form_title = 'Technical Advisor Application'
    block_content_slug = "ta_app"


class DataDisplaysAccessRequestView(BaseCustomFormView):
    """
        People can request access to the Data Displays
    """
    form_class = DataDisplayAccessRequestForm
    email_template_slug = "dd_application"
    form_title = 'Request Access to the Data Displays'
    block_content_slug = "dd_app"
