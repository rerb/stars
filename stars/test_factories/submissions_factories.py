import factory

from credits_factories import (ApplicabilityReasonFactory,
                               CategoryFactory,
                               CreditFactory,
                               CreditSetFactory,
                               DocumentationFieldFactory,
                               RatingFactory,
                               SubcategoryFactory)
from institutions_factories import ClimateZoneFactory, InstitutionFactory
from misc_factories import UserFactory
from stars.apps.submissions.models import (Boundary,
                                           CategorySubmission,
                                           CreditUserSubmission,
                                           DocumentationFieldSubmission,
                                           ResponsibleParty,
                                           SubcategorySubmission,
                                           SubmissionSet)


class ResponsiblePartyFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ResponsibleParty

    institution = factory.SubFactory(InstitutionFactory)
    first_name = 'Joe'
    last_name = factory.Sequence(lambda i: 'X{0}'.format(i))
    title = 'Ward'
    department = 'Responsibility'
    email = factory.Sequence(lambda i: 'joe{0}@ward.com'.format(i))
    phone = '1234567890'


class SubmissionSetFactory(factory.DjangoModelFactory):
    FACTORY_FOR = SubmissionSet

    creditset = factory.SubFactory(CreditSetFactory)
    institution = factory.SubFactory(InstitutionFactory)
    registering_user = factory.SubFactory(UserFactory)
    submitting_user = factory.SubFactory(UserFactory)
    rating = factory.SubFactory(RatingFactory)
    date_registered = '1970-01-01'

    @classmethod
    def _prepare(cls, create, **kwargs):
        """If this institution doesn't have any other,
        make this the current submission."""
        submission_set = super(SubmissionSetFactory, cls)._prepare(
            create, **kwargs)
        if not submission_set.institution.current_submission:
            submission_set.institution.current_submission = submission_set
            submission_set.institution.save()
        return submission_set


class CategorySubmissionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CategorySubmission

    submissionset = factory.SubFactory(SubmissionSetFactory)
    category = factory.SubFactory(CategoryFactory)


class SubcategorySubmissionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = SubcategorySubmission

    category_submission = factory.SubFactory(CategorySubmissionFactory)
    subcategory = factory.SubFactory(SubcategoryFactory)


class CreditUserSubmissionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CreditUserSubmission

    credit = factory.SubFactory(CreditFactory)
    subcategory_submission = factory.SubFactory(SubcategorySubmissionFactory)
    applicability_reason = factory.SubFactory(ApplicabilityReasonFactory)
    user = factory.SubFactory(UserFactory)
    responsible_party = factory.SubFactory(ResponsiblePartyFactory)


class DocumentationFieldSubmissionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DocumentationFieldSubmission

    documentation_field = factory.SubFactory(DocumentationFieldFactory)
    credit_submission = factory.SubFactory(CreditUserSubmissionFactory)


class BoundaryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Boundary

    submissionset = factory.SubFactory(SubmissionSetFactory)
    climate_region = factory.SubFactory(ClimateZoneFactory)
