from django.conf import settings
from django.core.mail import send_mail
from django.forms import ModelForm
from django.forms.fields import BooleanField
from django.template import Context
from django.template.loader import get_template

from stars.apps.custom_forms.models import EligibilityQuery, \
     SteeringCommitteeNomination, TAApplication, DataDisplayAccessRequest

from stars.apps.credits.models import Subcategory, CreditSet


class SteeringCommitteeNominationForm(ModelForm):

    class Meta:
        model = SteeringCommitteeNomination


class DataDisplayAccessRequestForm(ModelForm):

    class Meta:
        model = DataDisplayAccessRequest
        exclude = ['date']


class TAApplicationForm(ModelForm):

    class Meta:
        model = TAApplication
        # ordering
        fields = ["first_name", "last_name", "title", "department",
                  "institution", "phone_number", "email",
                  "instituion_type", "subcategories",
                  "skills_and_experience", "related_associations", "resume",
                  "credit_weakness"]

    def __init__(self, *args, **kwargs):

        super(TAApplicationForm, self).__init__(*args, **kwargs)

        self.fields['skills_and_experience'].label = """
            Describe what skills and experience you'd bring to the
            position"""

        self.fields['related_associations'].label = """
            List any related associations, committees, or
            organizations in which you are a member"""

        self.fields['resume'].label = "Upload a copy of your resume or CV"

        self.fields['credit_weakness'].label = """
            Briefly describe a weakness of a STARS credit or
            subcategory, including how it could be improved"""

        self.fields['subcategories'].label = """
            Select the STARS sub-categories for which you wish to
            serve as a Technical Advisor"""

        cs = CreditSet.objects.get_latest()
        subset = Subcategory.objects.filter(category__creditset=cs).exclude(
            title='Demo').exclude(
            title='Innovation').exclude(
            title='Institutional Characteristics')
        self.fields['subcategories'].choices = [(s.id, s.title) for s in subset]


class EligibilityForm(ModelForm):

    class Meta:
        model = EligibilityQuery

    def __init__(self, *args, **kwargs):

        super(EligibilityForm, self).__init__(*args, **kwargs)

        self.fields['requesting_institution'].label = """
            Institution or entity requesting consideration to register
            for STARS (if different from above):"""

        self.fields['other_affiliates'].label = """
            Are there other institutions or entities, affiliated with
            your institution, that are already participating in the
            STARS program?"""

        self.fields['included_in_boundary'].label = """
            If yes, is the institution or entity you are interested in
            registering for STARS included in the institutional
            boundary of this affiliated institution or entity's STARS
            Report?"""

        self.fields['separate_administration'].label = """
            Does the institution or entity requesting to register for
            STARS have a separate and/or distinct administration?"""

        self.fields['rationale'].label = """
            Please describe rationale for the STARS staff to consider
            when determining if the institution or entity requesting
            to register for STARS should be eligible to participate in
            the STARS program."""

    def send_email(self):

        responses = []
        for field_name, field in self.fields.items():
            value = getattr(self.instance, field_name)
            if isinstance(field, BooleanField):
                if value:
                    value = "YES"
                else:
                    value = "NO"
            responses.append({'label': field.label, 'value': value})

        _context = Context({'responses': responses,})
        t = get_template("custom_forms/eligibility_staff_email.txt")
        message = t.render(_context)

        email_to = ['stars@aashe.org',]
        send_mail("Eligibility Query from %s at %s" % (
            self.cleaned_data['name'], self.cleaned_data['institution']),
            message,
            self.cleaned_data['email'],
            email_to,
            fail_silently=False)

        t = get_template("custom_forms/eligibility_query_response.txt")
        message = t.render(_context)
        send_mail("Thank you for your enquiry",
                  message,
                  settings.EMAIL_HOST_USER,
                  [self.cleaned_data['email']],
                  fail_silently=False)
