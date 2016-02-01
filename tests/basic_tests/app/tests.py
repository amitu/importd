from __future__ import unicode_literals

from django.conf import settings
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase

import unittest
import os

from importd import env, NotSet, RaiseException


class BasicTest(TestCase):
    def setUp(self):
        try:
            self.root = User.objects.get(username="root")
        except User.DoesNotExist:
            self.root = User.objects.create_user(
                "root", "root@example.com", "root"
            )
        self.root.is_superuser = True
        self.root.is_active = True
        self.root.is_staff = True
        self.root.save()

    def test_settings_module(self):
        self.assertEqual(settings.SETTINGS_MODULE, "importd")

    def test_appdir(self):
        self.assertTrue(__file__.startswith(settings.APP_DIR + "/app/tests.py"))

    def test_debug(self):
        # django test sets up DEBUG to True, so this cant be tested like this.
        self.assertFalse(settings.DEBUG)

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
        # on windows, newline is CRLF.
        self.assertEqual(
            response.content.replace(b'\r', b''), b"<h1>test1: 42</h1>\n"
        )
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

        settings.DEBUG = True
        response = c.get("/static/404.css")
        self.assertEqual(response.status_code, 404)
        response = c.get("/static/style.css")
        self.assertEqual(response.status_code, 200)
        settings.DEBUG = False

    def test_static_outside_apps(self):
        c = Client()

        settings.DEBUG = True
        response = c.get("/static/generic.css")
        self.assertEqual(response.status_code, 200)
        settings.DEBUG = False

    def test_admin(self):
        c = Client()
        response = c.get("/admin/")

        # django < 1.7 returns 200, 1.7 returns 302, refer: http://goo.gl/9GTv9H
        self.assertIn(response.status_code, [200, 302])
        if response.status_code != 302:
            #self.assertEqual(  # TODO: Fix
                #[t.name for t in response.templates],
                #['admin/login.html', 'admin/base_site.html', 'admin/base.html']
            #)
            self.assertTrue(response.context["user"].is_anonymous())

        self.assertTrue(c.login(username="root", password="root"))

        response = None
        response = c.get("/admin/")
        self.assertEqual(response.status_code, 200)

        #self.assertEqual(  # TODO: Fix
            #[t.name for t in response.templates],
            #['admin/index.html', 'admin/base_site.html', 'admin/base.html']
        #)
        self.assertTrue(response.context["user"].is_authenticated())

    def test_namespace_url_reverse(self):
        url = reverse('app3:demo-url')
        self.assertEqual('/app3/demo/url', url)

    def test_view_with_blueprint(self):
        c = Client()
        response = c.get('/app3/demo/url')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'app3/demo-url')
        response = c.get('/app3/index3/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'app3/index')

    def test_use_same_blueprint_many_times(self):
        url = reverse('app3:demo-url')
        self.assertEqual('/app3/demo/url', url)
        url = reverse('app3-clone:demo-url')
        self.assertEqual('/app3-clone/demo/url', url)


class EnvTest(BasicTest):
    def test_env(self):
        old = os.environ
        os.environ = {}
        with self.assertRaises(KeyError):
            env("foo", default=RaiseException)
        os.environ = {"foo": "bar"}
        self.assertEqual(env("foo"), "bar")
        self.assertEqual(env("foo", default=False), True)
        self.assertEqual(env("foo", default=False, factory=NotSet), "bar")
        for v in ["0", "off", "Off", "False", "false", "no", "No"]:
            os.environ = {"IS_PROD": v}
            self.assertEqual(env("IS_PROD", default=False), False)
        os.environ = old
