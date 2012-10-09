from django.shortcuts import render
from django.views.generic.edit import FormView

from stars.apps.custom_forms.forms import EligibilityForm, \
     SteeringCommitteeNominationForm, TAApplicationForm
from stars.apps.helpers.mixins import ValidationMessageFormMixin
from stars.apps.notifications.models import EmailTemplate


class EligibilityView(ValidationMessageFormMixin, FormView):
    """
        View for the form that lets folks petition for STARS membership for
        an institution that doesn't qualify under the usual conditions.
    """

    form_class = EligibilityForm
    template_name = 'custom_forms/eligibility.html'

    def form_valid(self, form):
        form.send_email()
        return render(request=self.request,
                      template_name="custom_forms/form_success.html",
                      dictionary=self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(EligibilityView, self).get_context_data(**kwargs)
        context['form_title'] = 'Eligibility Inquiry'
        return context


class SteeringCommitteeNominationView(ValidationMessageFormMixin, FormView):
    """
       View for the form that lest folks apply to be sit on the STARS
       steering committee.
    """

    form_class = SteeringCommitteeNominationForm
    template_name = 'custom_forms/sc_app.html'

    def form_valid(self, form):
        form.save()
        et = EmailTemplate.objects.get(slug="sc_application")
        et.send_email([self.request.POST['email']], self.initial)
        return render(request=self.request,
                      template_name="custom_forms/form_success.html",
                      dictionary=self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(SteeringCommitteeNominationView,
                        self).get_context_data(**kwargs)
        context['form_title'] = 'STARS Steering Committee Nomination'
        return context


class TechnicalAdvisorApplicationView(ValidationMessageFormMixin, FormView):
    """
        View for the form that allows folks to apply to be STARS
        Techiical Advisors.
    """

    form_class = TAApplicationForm
    template_name = 'custom_forms/ta_app.html'

    def form_valid(self, form):
        form.save()
        et = EmailTemplate.objects.get(slug="ta_application")
        et.send_email([self.request.POST['email']], self.initial)
        return render(request=self.request,
                      template_name="custom_forms/form_success.html",
                      dictionary=self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(TechnicalAdvisorApplicationView,
                        self).get_context_data(**kwargs)
        context['form_title'] = 'Technical Advisor Application'
        return context
