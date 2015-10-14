import os

from django.test import TestCase
from django.conf import settings


class TestPathPy(TestCase):
    def test_path(self):
        path_with_py_api = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp-log.py")
        path_wit_d = settings.LOG_LOCATION
        self.assertEqual(path_with_py_api, path_wit_d)
