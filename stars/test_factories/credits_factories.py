import time

import factory

from stars.apps.credits.models import ApplicabilityReason, Category, \
     Credit, CreditSet, IncrementalFeature, Rating, Subcategory


class CreditSetFactory(factory.Factory):
    FACTORY_FOR = CreditSet

    release_date = '1970-01-01'
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

    @factory.post_generation(extract_prefix='supported_features')
    def add_supported_features(self, create, extracted, **kwargs):
        # allow something like CreditSetFactory(
        #     supported_features=IncrementalFeature.objects.filter(...))
        if extracted:
            self.supported_features = extracted


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
