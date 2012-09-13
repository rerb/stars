"""
    Unittests for the submission renewal process
"""
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from stars.apps.submissions.models import ResponsibleParty

class ResponisblePartyTest(TestCase):
    fixtures = ['responsible_party_test_data.json']

    def setUp(self):
        pass

    def test_delete(self):
        """

        """
        print self.fixtures
        user = User.objects.get(pk=1)
        user.set_password('test')
        user.save()

        c = Client()
        login = c.login(username='tester', password='test')
        self.assertTrue(login)

        rp = ResponsibleParty.objects.get(pk=1)

        rp_url = "/tool/{slug}/manage/responsible-parties/{id}/".format(
            slug=rp.institution.slug, id=rp.id)

        rp_del_url = \
          "/tool/{slug}/manage/responsible-parties/{id}/delete/".format(
              slug=rp.institution.slug, id=rp.id)

        # RP Page Loads... and RP exists
        response = c.get(rp_url)

        self.assertEqual(response.status_code, 200)

        # Delete should fail and redirect to RP
        response = c.get(rp_del_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            "http://testserver/tool/{slug}/manage/"
            "responsible-parties/{id}/".format(
                slug=rp.institution.slug, id=rp.id))

        # Confirm RP1 still exists
        self.assertEqual(ResponsibleParty.objects.count(), 2)

        rp = ResponsibleParty.objects.get(pk=2)

        rp_url = "/tool/{slug}/manage/responsible-parties/{id}/".format(
            slug=rp.institution.slug, id=rp.id)

        rp_del_url = \
          "/tool/{slug}/manage/responsible-parties/{id}/delete/".format(
              slug=rp.institution.slug, id=rp.id)

        # RP Page Loads... and RP exists
        response = c.get(rp_url)
        self.assertEqual(response.status_code, 200)

        # Delete should succeed and redirect to RP list
        response = c.get(rp_del_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            "http://testserver/tool/{slug}/manage/responsible-parties/".format(
                slug=rp.institution.slug))

        # Confirm RP2 still exists
        self.assertEqual(ResponsibleParty.objects.count(), 1)
