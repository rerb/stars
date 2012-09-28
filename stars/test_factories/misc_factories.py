import time

from django.contrib.auth.models import User
import factory


class UserFactory(factory.Factory):
    FACTORY_FOR = User

    username = factory.Sequence(
        lambda i: 'testuser-{0}.{1}'.format(i, time.time()))
    password = 'test'

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user
