import unittest

from django.contrib.auth.models import User

from stars.test_factories import accounts_factories

class UserProfileFactoryTest(unittest.TestCase):

    def test_user_is_created(self):
        user_profile = accounts_factories.UserProfileFactory()
        self.assertIsInstance(user_profile.user, 
                              User)
        
