from django.test import TestCase, Client
from django.conf import settings

class TestMirrorSettings(TestCase):
    def setUp(self):
        self.client = Client()

    def test_mirror_settings(self):
        self.assertEqual(settings.DEBUG_TEST, True)
