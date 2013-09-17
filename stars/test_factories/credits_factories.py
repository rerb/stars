import datetime
import time

import factory

from stars.apps.credits.models import (ApplicabilityReason, Category, Credit,
                                       CreditSet, DocumentationField,
                                       IncrementalFeature, Rating,
                                       Subcategory)


class RatingFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Rating

    minimal_score = 1


class TextDocumentationFieldFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DocumentationField

    type = 'text'


DocumentationFieldFactory = TextDocumentationFieldFactory


class CreditFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Credit

    id = factory.Sequence(int)
    identifier = factory.Sequence(lambda i: 'CREDIT-ID-{0}'.format(i))
    point_value = 1
    documentation_fields = factory.RelatedFactory(DocumentationFieldFactory,
                                                  'credit')
    

class SubcategoryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Subcategory

    id = factory.Sequence(int)
    title = factory.Sequence(lambda i: 'SUBCAT TITLE {0}'.format(i))
    credits = factory.RelatedFactory(CreditFactory, 'subcategory')


class CategoryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Category

    id = factory.Sequence(int)
    abbreviation = factory.Sequence(lambda i: int(str(i), 36))

    subcategories = factory.RelatedFactory(SubcategoryFactory, 'category')


class CreditSetFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CreditSet

    release_date = datetime.date(1970, 1, 1)
    tier_2_points = 1

    ratings = factory.RelatedFactory(RatingFactory, 'creditset')
    categories = factory.RelatedFactory(CategoryFactory, 'creditset')

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


class ApplicabilityReasonFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ApplicabilityReason

    credit = factory.SubFactory(CreditFactory)
    ordinal = factory.Sequence(lambda i: i)


class IncrementalFeatureFactory(factory.DjangoModelFactory):
    FACTORY_FOR = IncrementalFeature

    key = factory.Sequence(
        lambda i: 'factory-made-incr-feature-{0}-{1}'.format(i, time.time()))


