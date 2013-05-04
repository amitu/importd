from django.test import TestCase, Client
from django.contrib.auth.models import User
from importd import d

from test_app import TestModel

class ModelTest(TestCase):
    TEST_VALUE = "asdf"

    def setUp(self):
        self.c = Client()
        try:
            self.root = User.objects.get(username="root")
        except User.DoesNotExist:
            self.root = User.objects.create_user(
                "root", "root@example.com", "root"
            )
            self.root.is_superuser = True
            self.root.save()

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

    def test_admin(self):
        c = Client()
        response = c.get("/admin/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [t.name for t in response.templates], 
            ['admin/login.html', u'admin/base_site.html', u'admin/base.html']
        )
        self.assertTrue(response.context["user"].is_anonymous())
        self.assertTrue(c.login(username="root", password="root"))
        response = c.get("/admin/?a")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [t.name for t in response.templates], 
            ['admin/login.html', u'admin/base_site.html', u'admin/base.html']
            # FIXME: this is wrong
        )
        self.assertTrue(response.context["user"].is_authenticated())
        response = c.get("/admin/test_app_app/")
        self.assertEqual(response.status_code, 200)
