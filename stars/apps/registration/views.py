import abc
from logging import getLogger

from django.views.generic import CreateView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from aashe.issdjango.models import Organizations

from stars.apps.institutions.models import (Institution,
                                            RegistrationSurvey,
                                            RespondentSurvey)
from stars.apps.notifications.models import EmailTemplate
from stars.apps.registration.forms import (SelectSchoolForm,
                                           RegistrationSurveyForm,
                                           RespondentRegistrationSurveyForm,
                                           ContactForm)
from stars.apps.tool.mixins import InstitutionAdminToolMixin
from stars.apps.accounts.mixins import StarsAccountMixin

from .utils import init_starsaccount, init_submissionset
from ..payments.views import (SubscriptionPurchaseWizard,
                              amount_due_more_than_zero)


logger = getLogger('stars')


MEMBER = True
NON_MEMBER = False
BASE_REGISTRATION_PRICE = {MEMBER: 900, NON_MEMBER: 1400}


class RegistrationWizard(StarsAccountMixin, SubscriptionPurchaseWizard):
    """
        A wizard that runs a user through the forms required to register
        as a STARS Participant.

        This is an abstract class, by virtue of its abstract method
        picked_participant().

        Now that we're basing access on access levels (i.e., basic
        and full) rather than particpant status (participant or
        registerant), this code should be cleaned up to reflect
        the new terminology.  'picked_participant()', e.g., might
        better be replaced with 'access_level() == FULL'.  This cleanup
        is a post-2.0 launch task . . . typed 1.5 working days before
        launch of STARS 2.0.
    """
    __metaclass__ = abc.ABCMeta

    SELECT, CONTACT = 0, 1

    PRICE, PAYMENT_OPTIONS, SUBSCRIPTION_CREATE = 2, 3, 4

    REGISTRATION_FORMS = [(SELECT, SelectSchoolForm),
                          (CONTACT, ContactForm)]

    FORMS = SubscriptionPurchaseWizard.insert_forms_into_form_list(
        REGISTRATION_FORMS)

    TEMPLATES = {SELECT: 'registration/wizard_select.html',
                 PRICE: 'registration/wizard_price.html'}

    # Tack TEMPLATES from SubscriptionPurchaseWizard on the the end:
    for (key, value) in SubscriptionPurchaseWizard.TEMPLATES.items():
        TEMPLATES[key + len(REGISTRATION_FORMS)] = value

    def __init__(self, *args, **kwargs):
        self._institution = None
        super(RegistrationWizard, self).__init__(*args, **kwargs)

    @property
    def success_url(self):
        institution = self.get_institution()
        return reverse('reg_survey',
                       kwargs={'institution_slug': institution.slug})

    def get_institution(self):
        if not self._institution:
            self._institution = self.get_form_instance(str(self.CONTACT))
        return self._institution

    def get_template_names(self):
        if self.steps.current == str(self.CONTACT):
            return "registration/wizard_contact.html"
        elif self.steps.current == str(self.PRICE):
            return "registration/wizard_price.html"
        elif self.steps.current == str(self.PAYMENT_OPTIONS):
            return "registration/wizard_payment_options.html"
        elif self.steps.current == str(self.SUBSCRIPTION_CREATE):
            return "registration/wizard_subscription_create.html"
        return super(RegistrationWizard, self).get_template_names()

    def get_context_data(self, form, **kwargs):
        # First, something that has nothing to do with the context
        # data for the price step . . . here because it needs to be
        # called before the form is displayed . . .
        #
        # If the amount due is $0.00, we skip the payment steps.
        # Since amount_due_is_more_than_zero() checks the request.session
        # for the amount due, we'll clear it if it's already set.
        if self.steps.current == str(self.SELECT):
            try:
                del(self.request.session['amount_due'])
            except KeyError:
                pass

        context = super(RegistrationWizard, self).get_context_data(form=form,
                                                                   **kwargs)
        if self.steps.current == str(self.SUBSCRIPTION_CREATE):
            context.update({
                'institution': self.get_form_instance(str(self.CONTACT)),
                'contact': self.get_cleaned_data_for_step(str(self.CONTACT)),
                'new_registration': True})
        elif self.steps.current == str(self.SELECT + 1):
            # If the selected institution is already registered,
            # redirect to the tool summary page.  Then the user can be
            # surprised, maybe he didn't realize his institution as
            # already registered, or if he wants to purchase a
            # subscription, he can do that there, too.
            aashe_id = self.get_cleaned_data_for_step(
                str(self.SELECT))['aashe_id']
            try:
                inst = Institution.objects.get(aashe_id=aashe_id)
            except Institution.DoesNotExist:
                pass
            else:
                context['redirect'] = reverse(
                    'tool-summary',
                    kwargs={'institution_slug': inst.slug})
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
        if step == str(self.CONTACT):
            cleaned_data = (self.get_cleaned_data_for_step(str(self.SELECT))
                            or {})
            aashe_id = cleaned_data.get('aashe_id', None)
            org = Organizations.objects.get(account_num=aashe_id)
            institution = Institution(aashe_id=aashe_id, name=org.org_name)
            institution.update_from_iss()
            institution.set_slug_from_iss_institution(institution.aashe_id)
            return institution

        return None

    def process_step(self, form):
        if self.steps.current == self.PRICE:
            self.request.session['is_participant'] = self.picked_participant()
        return super(RegistrationWizard, self).process_step(form)
    
    @abc.abstractmethod
    def picked_participant(self):
        """ Checks if the user chose to be a participant """
        pass

    def done(self, form_list, **kwargs):
        institution = self.get_institution()

        if not institution.pk:
            institution.save()

        contact_form = form_list[self.CONTACT]

        self.update_institution_contact_info(institution,
                                             contact_form)
        self.update_institution_executive_contact_info(institution,
                                                       contact_form)

        init_starsaccount(self.request.user, institution)
        init_submissionset(institution, self.request.user)

        # 24 Oct 2013 - send_emails() sends "welcome_registrant"
        # email to all registrants, which is incorrect. Commenting
        # it out for now, until it's fixed (and sends "welcome_registrant"
        # to Basic Access folks, and "welcome_participant" to
        # Full Access subscribers.
        # self.send_emails(institution)

        return super(RegistrationWizard, self).done(form_list, **kwargs)

    def update_institution_contact_info(self, institution, contact_form):
        """Updates the contact info stored on Institution `institution`
        with info in form `contact_form`."""
        contact_field_names = ['contact_department',
                               'contact_email',
                               'contact_first_name',
                               'contact_last_name',
                               'contact_middle_name',
                               'contact_phone',
                               'contact_title']
        self._update_institution_contact_info(
            institution=institution,
            contact_field_names=contact_field_names,
            contact_form=contact_form)

    def update_institution_executive_contact_info(self,
                                                  institution,
                                                  contact_form):
        """Updates the exeutive contact info stored on Institution
        `institution` with info in form `contact_form`."""
        executive_contact_field_names = ['executive_contact_first_name',
                                         'executive_contact_last_name',
                                         'executive_contact_title',
                                         'executive_contact_department',
                                         'executive_contact_email']
        self._update_institution_contact_info(
            institution=institution,
            contact_field_names=executive_contact_field_names,
            contact_form=contact_form)

    def _update_institution_contact_info(self,
                                         institution,
                                         contact_field_names,
                                         contact_form):
        """Updates the fields with names in `contact_field_names` on
        Institution `institution` with input on form `contact_form`.
        """
        clean_form_info = contact_form.clean()
        for field_name in contact_field_names:
            setattr(institution,
                    field_name,
                    clean_form_info[field_name])
        institution.save()

    def send_emails(self, institution):
        # Primary Contact
        email_to = [institution.contact_email]

        if self.request.user.email != institution.contact_email:
            email_to.append(self.request.user.email)

        # Confirmation Email
        if institution.international:
            et = EmailTemplate.objects.get(
                slug='welcome_international_pilot')
            email_context = {'institution': institution}
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

    @classmethod
    def get_form_conditions(cls):
        form_conditions = {
            str(cls.PRICE): registerant_is_participant,
            str(cls.PAYMENT_OPTIONS): amount_due_more_than_zero,
            str(cls.SUBSCRIPTION_CREATE): registerant_is_participant}
        return form_conditions


def registerant_is_participant(wizard):
    """
    Under what condition should the payment forms be shown?  Why, when
    the user has chosen to be a participant, of course.  La la la.
    """
    return wizard.picked_participant()


class FullAccessRegistrationWizard(RegistrationWizard):

    def picked_participant(self):
        return True


class BasicAccessRegistrationWizard(RegistrationWizard):

    def picked_participant(self):
        return False


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
