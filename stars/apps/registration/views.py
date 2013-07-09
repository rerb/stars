from datetime import datetime
from logging import getLogger
import sys

from django.contrib import messages
from django.views.generic import CreateView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django import forms

from aashe.issdjango.models import Organizations

from stars.apps.institutions.models import (Institution,
                                            SubscriptionPayment,
                                            RegistrationSurvey,
                                            RespondentSurvey)
from stars.apps.notifications.models import EmailTemplate
from stars.apps.registration.forms import (SelectSchoolForm,
                                           ParticipationLevelForm,
                                           RegistrationPaymentForm,
                                           RegistrationSurveyForm,
                                           RespondentRegistrationSurveyForm,
                                           ContactForm)
from stars.apps.registration.models import ValueDiscount
from stars.apps.tool.mixins import InstitutionAdminToolMixin
from stars.apps.accounts.mixins import StarsAccountMixin
from stars.apps.helpers.wizard import BetterWizardView, RevalidationFailure

from utils import init_starsaccount, init_submissionset, init_subscription

from zc.authorizedotnet.processing import CcProcessor

logger = getLogger('stars')


REG_FORMS = [('select', SelectSchoolForm),
             ('level', ParticipationLevelForm),
             ('contact', ContactForm),
             ('payment', RegistrationPaymentForm)]


class RegistrationWizard(StarsAccountMixin, BetterWizardView):
    """
        A wizard that runs a user through the forms
        required to register as a STARS Participant
    """
    def get_template_names(self):
#        return "registration/wizard_base.html"
        if self.steps.current == 'contact':
            if self.picked_participant():
                return "registration/wizard_contact_participant.html"
            else:
                return "registration/wizard_contact_respondent.html"
        return ("registration/wizard_%s.html" % self.steps.current)

    def get_context_data(self, form, **kwargs):
        context = super(RegistrationWizard, self).get_context_data(form=form,
                                                                   **kwargs)
        if self.steps.current == 'payment':
            context.update({
                'institution': self.get_form_instance('contact'),
                'contact': self.get_cleaned_data_for_step('contact')})
        if self.steps.current == 'level':
            # redirect if they're already in the tool
            aashe_id = self.get_cleaned_data_for_step('select')['aashe_id']
            try:
                inst = Institution.objects.get(aashe_id=aashe_id)
                context['redirect'] = reverse('tool-summary',
                    kwargs={'institution_slug':
                            inst.slug})
            except:
                pass
        return context

    def render(self, form=None, **kwargs):
        """
        Returns a ``HttpResponse`` containing all needed context data.
        """
        form = form or self.get_form()
        context = self.get_context_data(form=form, **kwargs)
        if 'redirect' in context:
            return HttpResponseRedirect(context['redirect'])
        return self.render_to_response(context)

    def get_form_instance(self, step):
        """
            Create an instance for the contact form
            using the name from step 'select'
        """
        if step == 'contact':
            cleaned_data = self.get_cleaned_data_for_step('select') or {}
            aashe_id = cleaned_data.get('aashe_id', None)
            org = Organizations.objects.get(account_num=aashe_id)
            institution = Institution(aashe_id=aashe_id, name=org.org_name)
            institution.update_from_iss()
            institution.set_slug_from_iss_institution(institution.aashe_id)
            return institution

        return None

    def picked_participant(self):
        """ Checks if the user chose to be a participant """
        cleaned_data = self.get_cleaned_data_for_step('level') or {}
        return cleaned_data.get('level', None) == 'participant'

    def get_form_kwargs(self, step):
        """
            if the school is not going to be a participant then
            we don't need the executive contact information
        """
        kwargs = super(RegistrationWizard, self).get_form_kwargs(step)

        if step == 'contact':
            kwargs['include_exec'] = self.picked_participant()

        elif step == 'payment':
            institution = self.get_form_instance('contact')
            kwargs['amount'] = get_registration_price(institution,
                                                      new=True,
                                                      discount_code=None)
            kwargs['user'] = self.request.user
            kwargs['contact_info'] = self.get_cleaned_data_for_step('contact')
            kwargs['invoice_num'] = institution.aashe_id

        return kwargs

    def done(self, form_list, **kwargs):

        payment_form = None

        for form in form_list:
            # Get the Institution object
            if isinstance(form, ContactForm):
                institution = form.save(commit=False)

            # handle payment options
            if isinstance(form, RegistrationPaymentForm):
                payment_form = form

        response = self.finalize_registration(institution,
                                              payment_form,
                                              **kwargs)
        if response:
            return response

        return HttpResponseRedirect(
            reverse('reg_survey',
                    kwargs={'institution_slug': institution.slug}))

    def finalize_registration(self, institution, payment_form, **kwargs):
        """
            add_starsaccount
            init_submissionset
            init_subscription
            apply_payment
            send emails

            returns a response if necessary
        """

        payment = None
        amount_due = 0
        # Set up subscription and payment choice
        if self.picked_participant():

            if payment_form.cleaned_data['pay_later']:
                amount_due = payment_form.get_amount()
                institution.save()
                subscription = init_subscription(institution,
                                                 amount_due)
            else:
                # try to process the payment
                try:
                    confirmation = payment_form.process_payment()
                except forms.ValidationError, e:
                    messages.error(self.request,
                            ("Sorry, but this transaction did not clear."
                            " Reason: %s") % e)
                    raise RevalidationFailure("revalidate",
                                              'payment',
                                              payment_form,
                                              **kwargs)
#                    return self.render_revalidation_failure('payment',
#                                                            payment_form,
#                                                            **kwargs)
                institution.save()
                subscription = init_subscription(institution, amount_due)

                # add a SubscriptionPayment and process payment
                payment = SubscriptionPayment(subscription=subscription,
                                              date=datetime.now(),
                                              amount=payment_form.get_amount(),
                                              user=self.request.user,
                                              method='credit',
                                              confirmation=confirmation)
                payment.save()

        else:
            institution.save()

        init_starsaccount(self.request.user, institution)
        init_submissionset(institution, self.request.user)

        self.send_emails(institution, payment, amount_due)

    def send_emails(self, institution, payment, amount_due):

        # Primary Contact
        email_to = [institution.contact_email]

        if self.request.user.email != institution.contact_email:
            email_to.append(self.request.user.email)

        # Confirmation Email
        if institution.international:
            et = EmailTemplate.objects.get(slug='welcome_international_pilot')
            email_context = {'institution': institution}
        elif self.picked_participant():
            if payment == None:
                et = EmailTemplate.objects.get(slug='welcome_liaison_unpaid')
                email_context = {'price': amount_due}
            else:
                et = EmailTemplate.objects.get(slug='welcome_liaison_paid')
                email_context = {"institution": institution,
                                 'payment': payment}
        else:
            et = EmailTemplate.objects.get(slug='welcome_respondent')
            email_context = {"institution": institution}

        et.send_email(email_to, email_context)

        # Executive Contact
        if institution.executive_contact_email:
            email_to = [institution.executive_contact_email]
            if institution.international:
                et = EmailTemplate.objects.get(
                    slug='welcome_international_pilot_ec')
            else:
                et = EmailTemplate.objects.get(slug="welcome_exec")
            email_context = {"institution": institution}
            et.send_email(email_to, email_context)


def skip_payment_condition(wizard):
    """
        determines if the payment option can be skipped
    """
    return wizard.picked_participant()


participant_reg = RegistrationWizard.as_view(
    REG_FORMS,
    condition_dict={'payment': skip_payment_condition})


class SurveyView(InstitutionAdminToolMixin, CreateView):

    template_name = "registration/survey.html"

    @property
    def model(self):
        if self.get_institution().is_participant:
            return RegistrationSurvey
        else:
            return RespondentSurvey

    def get_form_kwargs(self):
        kwargs = super(SurveyView, self).get_form_kwargs()
        kwargs['instance'] = self.model(institution=self.get_institution(),
                                        user=self.request.user)
        return kwargs

    def get_form_class(self):
        if self.get_institution().is_participant:
            return RegistrationSurveyForm
        else:
            return RespondentRegistrationSurveyForm

    def get_success_url(self):
        return reverse('tool-summary',
                       kwargs={'institution_slug':
                               self.get_institution().slug})


def get_registration_price(institution, new=True, discount_code=None):
    """
        Calculates the registration price based on the institution.

        Coupon code should be evaluated beforehand. If the coupon code
        is not valid no discount will be assessed.
    """
    price = {'member': 900, 'non': 1400}

    discount = 0
    if discount_code:
        try:
            discount = ValueDiscount.objects.get(code=discount_code).amount
        except ValueDiscount.DoesNotExist:
            logger.warning("Invalid Coupon Code", exc_info=True)
            pass

    if institution.is_member:
        return price['member'] - discount
    else:
        return price['non'] - discount
