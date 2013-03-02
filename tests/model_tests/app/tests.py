from django.test import TestCase, Client
from importd import d

from test_app import TestModel

class ModelTest(TestCase):
    TEST_VALUE = "asdf"

    def setUp(self):
        self.c = Client()

    def test_addition(self):
        response = self.c.get("/add/{0}".format(self.TEST_VALUE))

        self.assertContains(response, "Success!")
        obj = TestModel.objects.get(value=self.TEST_VALUE)
        self.assertIsNotNone(obj)
        self.assertEqual(self.TEST_VALUE, obj.value)

    def test_model_getting(self):
        TestModel.objects.create(value=self.TEST_VALUE)
        response = self.c.get("/")

        self.assertContains(response, self.TEST_VALUE)