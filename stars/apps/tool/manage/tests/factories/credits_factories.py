import time

import factory

from stars.apps.credits.models import ApplicabilityReason, Category, \
     Credit, CreditSet, IncrementalFeature, Rating, Subcategory


class CreditSetFactory(factory.Factory):
    FACTORY_FOR = CreditSet

    version = factory.Sequence(lambda i: str(i))
    release_date = '1970-01-01'
    tier_2_points = 1

    @factory.post_generation(extract_prefix='incremental_features')
    def add_incremental_features(self, create, extracted, **kwargs):
        # allow something like CreditSetFactory(
        #     incremental_features=IncrementalFeature.objects.filter(...))
        if extracted:
            self.incremental_features = extracted


class CategoryFactory(factory.Factory):
    FACTORY_FOR = Category

    creditset = factory.SubFactory(CreditSetFactory)


class IncrementalFeatureFactory(factory.Factory):
    FACTORY_FOR = IncrementalFeature

    key = factory.Sequence(
        lambda i: 'factory-made-incr-feature-{0}-{1}'.format(i, time.time()))


class RatingFactory(factory.Factory):
    FACTORY_FOR = Rating

    creditset = factory.SubFactory(CreditSetFactory)
    minimal_score = 1


class SubcategoryFactory(factory.Factory):
    FACTORY_FOR = Subcategory

    category = factory.SubFactory(CategoryFactory)


class CreditFactory(factory.Factory):
    FACTORY_FOR = Credit

    subcategory = factory.SubFactory(SubcategoryFactory)
    point_value = 1


class ApplicabilityReasonFactory(factory.Factory):
    FACTORY_FOR = ApplicabilityReason

    credit = factory.SubFactory(CreditFactory)
    ordinal = factory.Sequence(lambda i: i)
