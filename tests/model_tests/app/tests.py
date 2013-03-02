from django.test import TestCase, Client
from importd import d


class ModelTest(TestCase):
    TEST_VALUE = "asdf"


    def setUp(self):
        self.c = Client()

    def test_addition(self):
        response = self.c.get("/add/{0}".format(self.TEST_VALUE))

        self.assertContains(response, "Success!")
        obj = d.models.TestModel.objects.get(value=self.TEST_VALUE)
        self.assertIsNotNone(obj)

    def test_model_getting(self):
        d.models.TestModel.objects.create(value=self.TEST_VALUE)
        response = self.c.get("/")

        self.assertContains(response, self.TEST_VALUE)