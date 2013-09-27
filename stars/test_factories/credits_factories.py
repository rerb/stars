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


class CreditSetFactory(factory.Factory):
    FACTORY_FOR = CreditSet

    release_date = datetime.date(1970, 1, 1)
    tier_2_points = 1

    _highest_version = 0

    @classmethod
    def _prepare(cls, create, **kwargs):
        """
            Assigns a (hopefully) unique version if no version is provided.
        """
        if 'version' not in kwargs:
            if CreditSet.objects.count():
                CreditSetFactory._highest_version = (
                    CreditSet.objects.all().order_by('-id')[0].id)
            else:
                CreditSetFactory._highest_version += 1
            kwargs['version'] = CreditSetFactory._highest_version
        credit_set = super(CreditSetFactory, cls)._prepare(create, **kwargs)
        return credit_set


class CategoryFactory(factory.Factory):
    FACTORY_FOR = Category

    creditset = factory.SubFactory(CreditSetFactory)


class SubcategoryFactory(factory.Factory):
    FACTORY_FOR = Subcategory

    category = factory.SubFactory(CategoryFactory)


class CreditFactory(factory.Factory):
    FACTORY_FOR = Credit

    subcategory = factory.SubFactory(SubcategoryFactory)
    point_value = 1


class UnitFactory(factory.Factory):
    FACTORY_FOR = Unit


class TextDocumentationFieldFactory(factory.Factory):
    FACTORY_FOR = DocumentationField

    credit = factory.SubFactory(CreditFactory)
    units = factory.SubFactory(UnitFactory)
    type = 'text'


DocumentationFieldFactory = TextDocumentationFieldFactory


class ApplicabilityReasonFactory(factory.Factory):
    FACTORY_FOR = ApplicabilityReason

    credit = factory.SubFactory(CreditFactory)
    ordinal = factory.Sequence(lambda i: i)


class RatingFactory(factory.Factory):
    FACTORY_FOR = Rating

    creditset = factory.SubFactory(CreditSetFactory)
    minimal_score = 1


