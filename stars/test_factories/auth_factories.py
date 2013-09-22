import factory

from aashe.aasheauth.models import AASHEUser
from stars.test_factories.misc_factories import UserFactory


class AASHEAccountFactory(factory.Factory):
    FACTORY_FOR = AASHEUser

    drupal_id = factory.Sequence(
        lambda i: str(i))
    drupal_session_key = factory.Sequence(
        lambda i: str(i))
    drupal_user_dict = {}

    user = factory.SubFactory(UserFactory)
