from mock import patch
from unittest import TestCase

from models import AASHEUser


class AASHEUserTest(TestCase):

    @patch(target=AASHEUser.get_drupal_user_dict,
           new=lambda: {'roles': 'Staff'})
    def test_update_staff_status_for_staff(self):
        """Does update_staff_status work for staff?"""
        aashe_user = AASHEUser()
        aashe_user.is_staff = True
        aashe_user.update_staff_status()
        self.assertTrue(aashe_user.is_staff)


if __name__ == '__main__':
    unittest.main()
