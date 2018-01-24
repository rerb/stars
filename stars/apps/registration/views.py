from logging import getLogger

from django.contrib.auth.models import User
from django.contrib.formtools.wizard.views import SessionWizardView
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import CreateView
from iss.models import Organization

from stars.apps.institutions.models import (Institution,
                                            RegistrationSurvey,
                                            RespondentSurvey)
from stars.apps.registration.forms import (SelectSchoolForm,
                                           RegistrationSurveyForm,
                                           RespondentRegistrationSurveyForm,
                                           InstitutionRegistrationForm)
from stars.apps.tool.mixins import InstitutionAdminToolMixin
from stars.apps.accounts.mixins import StarsAccountMixin
from stars.apps.notifications.models import EmailTemplate

from .utils import (init_starsaccount,
                    init_submissionset,
                    init_pending_starsaccount)


logger = getLogger('stars')


MEMBER = True
NON_MEMBER = False

FULL_ACCESS = 1
BASIC_ACCESS = 'use the constants, luke'

CONTACT_FIELD_NAMES = ['contact_department',
                       'contact_email',
                       'contact_first_name',
                       'contact_last_name',
                       'contact_phone',
                       'contact_title',
                       'executive_contact_first_name',
                       'executive_contact_last_name',
                       'executive_contact_title',
                       'executive_contact_department',
                       'executive_contact_email']

EXCLUDED_ORG_TYPE_ID = ('6faf90e4-000b-c40a-9b23-0b3c7f76be63',
                        '6faf90e4-000b-c639-9b81-0b3c7f76c336',)


class InstitutionCreateView(CreateView):

    model = Institution
    template_name = 'registration/new_institution.html'
    form_class = InstitutionRegistrationForm
    # for some reason, we do not have access to self.object in get_success_url
    # so I will set the slug to return inside of form_valid
    reverse_slug = None

    def get_context_data(self, **kwargs):
        context = super(InstitutionCreateView, self).get_context_data(**kwargs)
        institution_ids = Institution.objects.values_list('aashe_id',flat=True)
        institution_ids = [element for element in institution_ids
                           if element is not None]

        orgs = Organization.objects.exclude(org_type_id__in=EXCLUDED_ORG_TYPE_ID)
        orgs = orgs.exclude(account_num__in=institution_ids)
        orgs = (orgs.values('account_num', 'org_name', 'city')
            .order_by('org_name'))

        context['orgs'] = orgs
        return context

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.

        #if aashe_id is not set, it should return the form
        #return form_invalid
        if (str(self.request.POST.get('aashe_id')) == ''):
            form.add_selection_error()
            return self.form_invalid(form)

        aashe_id = str(self.request.POST.get('aashe_id'))
        aashe_id = int(aashe_id.replace(',',''))
        org = Organization.objects.get(account_num=aashe_id)
        institution = Institution(aashe_id=aashe_id, name=org.org_name)
        institution.update_from_iss()
        institution.set_slug_from_iss_institution(institution.aashe_id)

        # set contact info
        institution.contact_first_name = form.cleaned_data["contact_first_name"]
        institution.contact_last_name = form.cleaned_data["contact_last_name"]
        institution.contact_title = form.cleaned_data["contact_title"]
        institution.contact_department = form.cleaned_data["contact_department"]
        institution.contact_phone = form.cleaned_data["contact_phone"]
        institution.contact_email = form.cleaned_data["contact_email"]

        institution.executive_contact_first_name = form.cleaned_data["executive_contact_first_name"]
        institution.executive_contact_last_name = form.cleaned_data["executive_contact_last_name"]
        institution.executive_contact_title = form.cleaned_data["executive_contact_title"]
        institution.executive_contact_department = form.cleaned_data["executive_contact_department"]
        institution.executive_contact_email = form.cleaned_data["executive_contact_email"]

        institution.save()

        self.return_slug = institution.slug

        if(str(self.request.user.email) == str(institution.contact_email)):
                self.set_up_account(person=self.request.user, institution=institution)
                self.set_up_submissionset(person=self.request.user, institution=institution)
        elif(User.objects.filter(email=institution.contact_email).exists()):
            liaison = User.objects.get(email=institution.contact_email)
            self.set_up_account(person=self.request.user, institution=institution)
            self.set_up_submissionset(person=self.request.user, institution=institution)
            self.set_up_account(person=liaison, institution=institution)
        else:
            self.set_up_account(person=self.request.user, institution=institution)
            self.set_up_submissionset(person=self.request.user, institution=institution)
            self.set_up_pending_account(person=institution.contact_email, institution=institution)

        et = EmailTemplate.objects.get(slug='welcome_respondent')
        et.send_email(
            [institution.contact_email, institution.executive_contact_email],
            {'institution': institution})

        return super(InstitutionCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('tool-summary',
                       kwargs={'institution_slug': self.return_slug})

    def set_up_account(self, person, institution):
        """
            Set up the admin account for user provided
        """
        try:
            account = init_starsaccount(person, institution)
        except Exception as exc:
            delete_objects([institution])
            try:
                delete_objects([account])
            except UnboundLocalError:
                pass
            raise exc

    def set_up_submissionset(self, person, institution):
        """
            Initializes submissionset with provided User
        """
        try:
            submissionset = init_submissionset(institution, person)
        except Exception as exc:
            delete_objects([institution, account])
            try:
                delete_objects([submissionset])
            except UnboundLocalError:
                pass
            raise exc

    def set_up_pending_account(self, person, institution):
        """
            If there is no User record for liaison, set up a PendingAccount
        """
        try:
            account = init_pending_starsaccount(person, institution)
        except Exception as exc:
            delete_objects([institution])
            try:
                delete_objects([account])
            except UnboundLocalError:
                pass
            raise exc


class RegistrationWizard(StarsAccountMixin, SessionWizardView):
    """
        A wizard that runs a user through the forms required to register
        for STARS.
    """
    SELECT, CONTACT = 0, 1

    FORMS = [(SELECT, SelectSchoolForm),
             (CONTACT, InstitutionRegistrationForm)]

    TEMPLATES = {SELECT: 'registration/wizard_select.html',
                 CONTACT: 'registration/wizard_contact.html'}

    def __init__(self, *args, **kwargs):
        self._institution = None
        super(RegistrationWizard, self).__init__(*args, **kwargs)

    @property
    def success_url(self):
        institution = self.get_institution()
        return reverse('reg_survey',
                       kwargs={'institution_slug': institution.slug})

    @classmethod
    def get_class_form_list(cls):
        return [form[1] for form in cls.FORMS]

    def get_template_names(self):
        return [self.TEMPLATES[int(self.steps.current)]]

    def get_context_data(self, form, **kwargs):
        context = super(RegistrationWizard, self).get_context_data(
            form=form, kwargs=kwargs)
        if self.steps.current == str(self.SELECT + 1):
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

    def process_step(self, form):
        if int(self.steps.current) == self.CONTACT:
            self._process_step_contact_info(form)
        return super(RegistrationWizard, self).process_step(form)

    def get_institution(self):
        if not self._institution:
            self._institution = self.get_form_instance(str(self.CONTACT))
        return self._institution

    def _process_step_contact_info(self, form):

        clean_form_info = form.clean()

        for contact_field_name in CONTACT_FIELD_NAMES:
            self.request.session[contact_field_name] = clean_form_info[
                contact_field_name]

        institution = self.get_institution()

        self.update_institution_contact_info(institution)

        # institution must have a pk before creating related StarsAccount
        # and SubmissionSet records, so save it now:
        institution.save()

        try:
            account = init_starsaccount(self.request.user, institution)
        except Exception as exc:
            delete_objects([institution])
            raise exc

        try:
            init_submissionset(institution, self.request.user)
        except Exception as exc:
            delete_objects([institution, account])
            raise exc

        # now send the email
        et = EmailTemplate.objects.get(slug='welcome_respondent')
        et.send_email(
            [institution.contact_email], {'institution': institution})

    def update_institution_contact_info(self, institution):
        """Updates the contact info stored on Institution `institution`
        with info in form `contact_form`."""
        for field_name in CONTACT_FIELD_NAMES:
            setattr(institution,
                    field_name,
                    self.request.session[field_name])

    def done(self, forms, **kwargs):
        return HttpResponseRedirect(self.success_url)


def delete_objects(dead_men_walking):
    for dead_man in dead_men_walking:
        try:
            dead_man.delete()
        except ObjectDoesNotExist:
            pass


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
