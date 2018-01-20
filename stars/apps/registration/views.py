import abc
from logging import getLogger

from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import CreateView, TemplateView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render

from iss.models import Organization

from stars.apps.institutions.models import (Institution,
                                            RegistrationSurvey,
                                            RespondentSurvey)
from stars.apps.registration.forms import (SelectSchoolForm,
                                           RegistrationSurveyForm,
                                           RespondentRegistrationSurveyForm,
                                           ContactForm,
                                           InstitutionRegistrationForm,)
from stars.apps.tool.mixins import InstitutionAdminToolMixin
from stars.apps.accounts.mixins import StarsAccountMixin
from stars.apps.notifications.models import EmailTemplate

from .utils import init_starsaccount, init_submissionset
from ..payments.views import (FAILURE,
                              SubscriptionPurchaseWizard,
                              amount_due_more_than_zero)


logger = getLogger('stars')


MEMBER = True
NON_MEMBER = False
BASE_REGISTRATION_PRICE = {MEMBER: 900, NON_MEMBER: 1400}

FULL_ACCESS = 1
BASIC_ACCESS = 'use the constants, luke'

CONTACT_FIELD_NAMES = ['contact_department',
                       'contact_email',
                       'contact_first_name',
                       'contact_last_name',
                       'contact_middle_name',
                       'contact_phone',
                       'contact_title',
                       'executive_contact_first_name',
                       'executive_contact_last_name',
                       'executive_contact_title',
                       'executive_contact_department',
                       'executive_contact_email']

BUSINESS_ORG_TYPE_ID = ('6faf90e4-000b-c40a-9b23-0b3c7f76be63',)

class InstitutionCreateView(CreateView):

    model = Institution
    template_name = 'registration/new_institution.html'
    form_class = InstitutionRegistrationForm

    def get_context_data(self, **kwargs):
        context = super(InstitutionCreateView, self).get_context_data(**kwargs)
        contact_form = self.get_form_class()
        institution_ids = Institution.objects.values_list('aashe_id',flat=True)
        institution_ids = [element for element in institution_ids
                           if element is not None]

        orgs = Organization.objects.exclude(org_type_id__in=BUSINESS_ORG_TYPE_ID)
        orgs = orgs.exclude(account_num__in=institution_ids)
        orgs = orgs.values('account_num', 'org_name').order_by('org_name')

        context['contact_form'] = contact_form
        context['orgs'] = orgs
        return context

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.

        #if aashe_id is not set, it should return the form
        #return form_invalid

        aashe_id = str(self.request.POST.get('aashe_id'))
        aashe_id = int(aashe_id.replace(',',''))
        org = Organization.objects.get(account_num=aashe_id)
        institution = Institution(aashe_id=aashe_id, name=org.org_name)
        institution.update_from_iss()
        institution.set_slug_from_iss_institution(institution.aashe_id)

        # set contact info
        institution.contact_first_name = form.fields["contact_first_name"]
        institution.contact_last_name = form.fields["contact_last_name"]
        institution.contact_title = form.fields["contact_title"]
        institution.contact_department = form.fields["contact_department"]
        institution.contact_phone = form.fields["contact_phone"]
        institution.contact_email = form.fields["contact_email"]

        institution.executive_contact_first_name = form.fields["executive_contact_first_name"]
        institution.executive_contact_last_name = form.fields["executive_contact_last_name"]
        institution.executive_contact_title = form.fields["executive_contact_title"]
        institution.executive_contact_department = form.fields["executive_contact_department"]
        institution.executive_contact_email = form.fields["executive_contact_email"]

        institution.save()

        try:
            account = init_starsaccount(self.request.user, institution)
        except Exception as exc:
            delete_objects([institution])
            try:
                delete_objects([account])
            except UnboundLocalError:
                pass
            raise exc

        try:
            submissionset = init_submissionset(institution, self.request.user)
        except Exception as exc:
            delete_objects([institution, account])
            try:
                delete_objects([submissionset])
            except UnboundLocalError:
                pass
            raise exc


        return super(InstitutionRegistrationForm, self).form_valid(form)

    def get_success_url(self):
        institution = self.object
        return reverse('reg_survey',
                       kwargs={'institution_slug': institution.slug})




class RegistrationWizard(StarsAccountMixin, SubscriptionPurchaseWizard):
    """
        A wizard that runs a user through the forms required to register
        for STARS.

        This is an abstract class, by virtue of its abstract property
        access_level.
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
            org = Organization.objects.get(account_num=aashe_id)
            institution = Institution(aashe_id=aashe_id, name=org.org_name)
            institution.update_from_iss()
            institution.set_slug_from_iss_institution(institution.aashe_id)
            return institution

        return None

    @abc.abstractproperty
    def access_level(self):
        """What access level is this person registering for?"""
        pass

    def process_step(self, form):
        if int(self.steps.current) == self.CONTACT:
            self._process_step_contact_info(form)
        return super(RegistrationWizard, self).process_step(form)

    def _process_step_contact_info(self, form):
        """Save the contact info so we'll have it to pop into the
        Institution later, when it's finally created.
        """
        clean_form_info = form.clean()
        for contact_field_name in CONTACT_FIELD_NAMES:
            self.request.session[contact_field_name] = clean_form_info[
                contact_field_name]

    def update_institution_contact_info(self, institution):
        """Updates the contact info stored on Institution `institution`
        with info in form `contact_form`."""
        for field_name in CONTACT_FIELD_NAMES:
            setattr(institution,
                    field_name,
                    self.request.session[field_name])

    @classmethod
    def get_form_conditions(cls):
        """Returns a dictionary of conditionally displayed forms and
        the conditional which must evaluate to True for the form to be
        shown.
        """
        form_conditions = {
            str(cls.PRICE): registering_for_full_access,
            str(cls.PAYMENT_OPTIONS): amount_due_more_than_zero,
            str(cls.SUBSCRIPTION_CREATE): registering_for_full_access}
        return form_conditions


def registering_for_full_access(wizard):
    """Returns True if this registration is for Full Access,
    False otherwise.
    """
    return wizard.access_level == FULL_ACCESS


def delete_objects(dead_men_walking):
    for dead_man in dead_men_walking:
        try:
            dead_man.delete()
        except ObjectDoesNotExist:
            pass


class FullAccessRegistrationWizard(RegistrationWizard):

    @property
    def access_level(self):
        return FULL_ACCESS

    def _process_step_subscription_create(self, form):

        institution = self.get_institution()

        self.update_institution_contact_info(institution)

        # institution must have a pk before creating related StarsAccount
        # and SubmissionSet records, so save it now:
        institution.save()

        try:
            account = init_starsaccount(self.request.user, institution)
        except Exception as exc:
            delete_objects([institution])
            try:
                delete_objects([account])
            except UnboundLocalError:
                pass
            raise exc

        try:
            submissionset = init_submissionset(institution, self.request.user)
        except Exception as exc:
            delete_objects([institution, account])
            try:
                delete_objects([submissionset])
            except UnboundLocalError:
                pass
            raise exc

        try:
            result = super(FullAccessRegistrationWizard,
                           self)._process_step_subscription_create(form)
        except:
            delete_objects([account, submissionset, institution])
            raise
        else:
            if result == FAILURE:
                delete_objects([account, submissionset, institution])


class BasicAccessRegistrationWizard(RegistrationWizard):

    @property
    def access_level(self):
        return BASIC_ACCESS

    def _process_step_contact_info(self, form):
        super(BasicAccessRegistrationWizard,
              self)._process_step_contact_info(form)

        institution = self.get_institution()

        self.update_institution_contact_info(institution)

        # institution must have a pk before creating related StarsAccount
        # and SubmissionSet records, so save it now:
        institution.save()

        try:
            account = init_starsaccount(self.request.user, institution)
        except Exception as exc:
            delete_objects([institution])
            try:
                delete_objects([account])
            except UnboundLocalError:
                pass
            raise exc

        try:
            submissionset = init_submissionset(institution, self.request.user)
        except Exception as exc:
            delete_objects([institution, account])
            try:
                delete_objects([submissionset])
            except UnboundLocalError:
                pass
            raise exc

        # now send the email
        et = EmailTemplate.objects.get(slug='welcome_respondent')
        et.send_email(
            [institution.contact_email], {'institution': institution})


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
