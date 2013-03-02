from django.utils import unittest
from django.conf import settings
from django.test.client import Client
from django.core.urlresolvers import resolve

import os

class BasicTest(unittest.TestCase):
    def test_appdir(self):
        self.assertTrue(__file__.startswith(settings.APP_DIR + "/app/tests.py"))

    def test_debug(self):
        # django test sets up DEBUG to True, so this cant be tested like this.
        # self.assertTrue(settings.DEBUG)
        pass

    def test_insalled_apps(self):
        self.assertEqual(["app"], settings.INSTALLED_APPS)

    def test_views_imported(self):
        self.assertTrue(settings.VIEWS_IMPORTED)

    def test_signals_imported(self):
        self.assertTrue(settings.SIGNALS_IMPORTED)

    def test_forms_imported(self):
        self.assertTrue(settings.FORMS_IMPORTED)

    def test_static_mapped(self):
        self.assertEqual(
            resolve("/static/").url_name, 
            "django.contrib.staticfiles.views.serve"
        )
        settings.DEBUG=True
        c = Client()
        response = c.get("/static/404.css")
        self.assertEqual(response.status_code, 404)
        response = c.get("/static/style.css")
        self.assertEqual(response.status_code, 200)
        settings.DEBUG=False

