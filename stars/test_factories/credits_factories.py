import datetime
import time

import factory

from stars.apps.credits.models import (ApplicabilityReason,
                                       Category,
                                       Credit,
                                       CreditSet,
                                       DocumentationField,
                                       IncrementalFeature,
                                       Rating,
                                       Subcategory,
                                       Unit)


class CreditSetFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CreditSet

    version = factory.Sequence(lambda i: i)
    release_date = datetime.date(1970, 1, 1)
    tier_2_points = 1


class CategoryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Category

    creditset = factory.SubFactory(CreditSetFactory)


class SubcategoryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Subcategory

    category = factory.SubFactory(CategoryFactory)


class CreditFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Credit

    subcategory = factory.SubFactory(SubcategoryFactory)
    point_value = 1


class UnitFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Unit


class TextDocumentationFieldFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DocumentationField

    credit = factory.SubFactory(CreditFactory)
    units = factory.SubFactory(UnitFactory)
    type = 'text'


DocumentationFieldFactory = TextDocumentationFieldFactory


class ApplicabilityReasonFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ApplicabilityReason

    credit = factory.SubFactory(CreditFactory)
    ordinal = factory.Sequence(lambda i: i)


class RatingFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Rating

    creditset = factory.SubFactory(CreditSetFactory)
    minimal_score = 1


