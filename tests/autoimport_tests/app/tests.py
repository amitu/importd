from __future__ import unicode_literals

from django.test.client import Client
from django.test import TestCase
from django.conf import settings


class AutoImportTest(TestCase):

    def test_autoimport(self):
        c = Client()
        response = c.get("/view/")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(settings.SETTINGS_MODULE, "main")
