import datetime
import time

import factory

from stars.apps.credits.models import (ApplicabilityReason, Category, Credit,
                                       CreditSet, DocumentationField,
                                       IncrementalFeature, Rating,
                                       Subcategory)


class CreditSetFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CreditSet

    release_date = datetime.date(1970, 1, 1)
    tier_2_points = 1

    @classmethod
    def _prepare(cls, create, **kwargs):
        """
            Assigns a (hopefully) unique version if no version is provided.
        """
        if ('version' not in kwargs and
            CreditSet.objects.count()):
            highest_version = CreditSet.objects.all().order_by('-id')[0].id
            kwargs['version'] = int(highest_version) + 1
        credit_set = super(CreditSetFactory, cls)._prepare(create, **kwargs)
        return credit_set


class CategoryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Category

    creditset = factory.SubFactory(CreditSetFactory)
    id = factory.Sequence(int)
    abbreviation = factory.Sequence(lambda i: int(str(i), 36))


class IncrementalFeatureFactory(factory.DjangoModelFactory):
    FACTORY_FOR = IncrementalFeature

    key = factory.Sequence(
        lambda i: 'factory-made-incr-feature-{0}-{1}'.format(i, time.time()))


class RatingFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Rating

    creditset = factory.SubFactory(CreditSetFactory)
    minimal_score = 1


class SubcategoryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Subcategory

    category = factory.SubFactory(CategoryFactory)
    id = factory.Sequence(int)
    title = factory.Sequence(lambda i: 'SUBCAT TITLE {0}'.format(i))


class CreditFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Credit

    id = factory.Sequence(int)
    identifier = factory.Sequence(lambda i: 'CREDIT-ID-{0}'.format(i))
    point_value = 1
    subcategory = factory.SubFactory(SubcategoryFactory)


class TextDocumentationFieldFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DocumentationField

    credit = factory.SubFactory(CreditFactory)
    type = 'text'


DocumentationFieldFactory = TextDocumentationFieldFactory


class ApplicabilityReasonFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ApplicabilityReason

    credit = factory.SubFactory(CreditFactory)
    ordinal = factory.Sequence(lambda i: i)
