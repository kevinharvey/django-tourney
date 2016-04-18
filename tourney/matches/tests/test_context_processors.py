from django.test import TestCase, RequestFactory
from django.http import HttpResponse

from matches.context_processors import add_site_settings


class AddSiteSettingsContextProcessorTestCase(TestCase):

    def setUp(self, *args, **kwargs):
        self.factory = RequestFactory()

    def test_basics(self):
        """
        Test that we add the 'SITE_NAME' key to the context
        """
        request = self.factory.get('/')

        with self.settings(SITE_NAME='My Tourney Site'):
            context = add_site_settings(request)

            self.assertEqual(context['SITE_NAME'], 'My Tourney Site')
