import os

from django.test import TestCase
from django.conf import settings


class TestPathPy(TestCase):
    def test_path(self):
        path_with_py_api = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp-log.py")
        path_wit_d = os.path.join(settings.LOG_LOCATION, "test_app", "temp-log.py")
        self.assertEqual(path_with_py_api, str(path_wit_d))
