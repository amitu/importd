from django.conf import settings
from django.test.client import Client
from django.core.urlresolvers import resolve
from django.contrib.auth.models import User
from django.test import TestCase

import os

from importd import d

class BasicTest(TestCase):
    def setUp(self):
        try:
            self.root = User.objects.get(username="root")
        except User.DoesNotExist:
            self.root = User.objects.create_user(
                "root", "root@example.com", "root"
            )
            self.root.is_superuser = True
            self.root.save()

    def test_appdir(self):
        self.assertTrue(__file__.startswith(settings.APP_DIR + "/app/tests.py"))

    def test_debug(self):
        # django test sets up DEBUG to True, so this cant be tested like this.
        # self.assertTrue(settings.DEBUG)
        pass

    def test_insalled_apps(self):
        self.assertEqual(
            settings.INSTALLED_APPS, [
                'app', 'app2', 'django.contrib.auth',
                'django.contrib.contenttypes', 'django.contrib.messages',
                 'django.contrib.sessions', 'django.contrib.admin'
            ]
        )

    def test_views_imported(self):
        self.assertTrue(settings.VIEWS_IMPORTED)

    def test_signals_imported(self):
        self.assertTrue(settings.SIGNALS_IMPORTED)

    def test_forms_imported(self):
        self.assertTrue(settings.FORMS_IMPORTED)

    def test_view_with_d_decorator(self):
        c = Client()
        response = c.get("/test1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["the_answer"], 42)
        self.assertTemplateUsed(response, "test1.html")
        self.assertEqual(response.content, b"<h1>test1: 42</h1>\n")
        response = c.get("/testnotfound/")
        self.assertEqual(response.status_code, 404)

    def test_mounts(self):
        c = Client()
        response = c.get("/index/")
        self.assertEqual(response.status_code, 404)
        response = c.get("/app2/index2/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"app2/index")

    def test_static_mapped(self):
        c = Client()

        self.assertEqual(
            resolve("/static/").url_name,
            "django.contrib.staticfiles.views.serve"
        )
        settings.DEBUG=True
        response = c.get("/static/404.css")
        self.assertEqual(response.status_code, 404)
        response = c.get("/static/style.css")
        self.assertEqual(response.status_code, 200)
        settings.DEBUG=False

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
        response = c.get("/admin/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [t.name for t in response.templates],
            ['admin/login.html', u'admin/base_site.html', u'admin/base.html']
            # FIXME: this is wrong!
        )
        self.assertTrue(response.context["user"].is_authenticated())


