# -*- coding: utf-8 -*-


# metadata
""" Importd django based mini framework """
__license__ = 'BSD'
__author__ = 'Amit Upadhyay'
__url__ = 'http://amitu.com/importd'
__docformat__ = 'html'
__source__ = 'https://github.com/amitu/importd'


# stdlib imports
import inspect
import os
import sys
from getpass import getuser
from platform import python_version
from random import sample
from string import ascii_letters, digits

# django imports
import django.core.urlresolvers
from django.conf import global_settings, settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.core import management
from django.forms import forms
from django.shortcuts import render_to_response
from django.template import RequestContext

# importd and fhurl imports
import dj_database_url
from fhurl import JSONResponse
from importd import urlconf

# custom imports
try:
    import importlib
except ImportError:
    from django.utils import importlib  # lint:ok
try:
    import debug_toolbar  # lint:ok
    DEBUG_TOOLBAR = True
except ImportError:
    DEBUG_TOOLBAR = False
try:
    from django.http.response import HttpResponseBase as HttpResponse_base_obj
except ImportError:
    from django.http import HttpResponse as HttpResponse_base_obj  # lint:ok
try:
    from django.core.wsgi import get_wsgi_application
except ImportError:
    import django.core.handlers.wsgi
try:
    from django.conf.urls.defaults import patterns, url
except ImportError:
    from django.conf.urls import patterns, url  # lint:ok
try:
    from django.conf.urls import include
except ImportError:
    from django.conf.urls.defaults import include  # lint:ok
try:
    from speaklater import make_lazy_string
    LAZY_STRING = True
except ImportError:
    LAZY_STRING = False


if python_version().startswith('3'):
    basestring = unicode = str  # lint:ok


###############################################################################


class SmartReturnMiddleware(object):
    """
    Smart response middleware for views. Converts view return to the following:
    HttpResponse - stays the same
    string - renders the template named in the string
    (string, dict) - renders the template with keyword arguments.
    object - renders JSONResponse of the object
    """

    def process_view(self, request, view_func, view_args, view_kwargs):

        res = view_func(request, *view_args, **view_kwargs)
        if isinstance(res, basestring):
            res = res, {}
        if isinstance(res, HttpResponse_base_obj):
            return res
        if isinstance(res, tuple):
            template_name, context = res
            res = render_to_response(
                template_name, context, RequestContext(request)
            )
        else:
            res = JSONResponse(res)
        return res


###############################################################################


class D(object):
    urlpatterns = urlconf.urlpatterns

    def _is_management_command(self, command):
        return command in ("runserver", "shell")

    def _handle_management_command(self, cmd, *args, **kw):
        if not hasattr(self, "_configured"):
            self._configure_django(DEBUG=True)
        management.call_command(cmd, *args, **kw)

    def update_regexers(self, regexers):
        self.regexers.update(regexers)

    def update_urls(self, urls):
        self.urlpatterns += urls

    # tuple list of django modules imported in d
    # tuple (a, b) is equivalent to from a import b
    # if b is an iterable (b = [c, d]), it is equivalent
    # to from a import c, d
    DJANGO_IMPORT = (
        ('smarturls', 'surl'),
        ('django.http', ['HttpResponse', 'Http404', 'HttpResponseRedirect']),
        ('django.shortcuts', ['get_object_or_404', 'get_list_or_404',
                              'render_to_response', 'render', 'redirect']),
        ('django.template', 'RequestContext'),
        ('django', 'forms'),
        ('fhurl', ['RequestForm', 'fhurl', 'JSONResponse']),
        ('django.db.models', ''),
    )

    def _iterate_imports(self, callback):
        """
            Iterates through imports and calls callback for each
            (module_name, attributes) pair. If attribute is a string, it is
            converted to a list first. Empty strings become empty lists
        """

        for module_name, attributes in self.DJANGO_IMPORT:
            if isinstance(attributes, basestring):
                if attributes:
                    attributes = [attributes]
                else:
                    attributes = []
            callback(module_name, attributes)

    def _import_django(self):

        def set_attr(module_name, attributes):
            module = importlib.import_module(module_name)
            if attributes:
                for attribute in attributes:
                    setattr(self, attribute, getattr(module, attribute))
            else:
                setattr(self, module_name.split(".")[-1], module)
        self._iterate_imports(set_attr)

        try:
            self.wsgi_application = get_wsgi_application()
        except ImportError:

            self.wsgi_application = django.core.handlers.wsgi.WSGIHandler()

        self.patterns = patterns
        self.url = url

    def _get_app_dir(self, pth):
        return os.path.join(self.APP_DIR, pth)

    def dotslash(self, _path):
        """Returns the ./ directory"""
        if hasattr(self, "APP_DIR"):
            dotslash_path = self._get_app_dir(_path=_path)
        elif LAZY_STRING:
            dotslash_path = make_lazy_string(self._get_app_dir, _path)
        else:
            raise RuntimeError("Configure django, or install speaklater.")
        return dotslash_path

    def generate_mount_url(self, regex, v_or_f, mod):
        # self.mounts can be None, which means no url generation,
        # url is being managed by urlpatterns.
        # else self.mounts is a dict, containing app name and where to mount
        # if where it mount is None then again don't mount this fellow
        if getattr(self, "mounts", None) is None:
            return  # we don't want to mount anything
        if not regex.startswith("/"):
            return regex

        if not mod:
            if isinstance(v_or_f, basestring):
                mod = v_or_f
            else:  # if hasattr(v_or_f, "__module__")?
                mod = v_or_f.__module__

        best_k, best_v = "", None

        for k, v in self.mounts.items():
            if mod.startswith(k) and len(k) > len(best_k):
                best_k = k
                best_v = v

        if best_k:
            if not best_v:
                return
            if not best_v.endswith("/"):
                best_k += "/"
            if best_v != "/":
                regex = best_v[:-1] + regex

        return regex

    def add_view(self, regex, view, app=None, *args, **kw):
        regex = self.generate_mount_url(regex, view, app)
        if regex:
            self.urlpatterns += self.patterns(
                "", self.surl(regex, view, *args, **kw)
            )
            django.core.urlresolvers.clear_url_caches()

    def add_form(self, regex, form_cls, app=None, *args, **kw):
        regex = self.generate_mount_url(regex, form_cls, app)
        if regex:
            self.urlpatterns.append(self.fhurl(regex, form_cls, *args, **kw))
            django.core.urlresolvers.clear_url_caches()

    def get_secret_key(self):
        """get a django secret key,try to read provided one,else generate it"""
        try:
            with open(self.dotslash("secret.txt"), "r") as f:
                secret = f.readlines()[0].strip()
        except (IOError, IndexError):
            with open(self.dotslash("secret.txt"), "w") as f:
                secret = "".join(sample(ascii_letters + digits, 50))
                f.write(secret)
        finally:
            return secret

    def _configure_django(self, **kw):

        self.settings = settings
        if settings.configured:
            return

        self.APP_DIR, app_filename = os.path.split(
            os.path.realpath(inspect.stack()[2][1])
        )

        if "regexers" in kw:
            self.update_regexers(kw.pop("regexers"))

        self.mounts = kw.pop("mounts", {})

        if not kw.get("dont_configure", False):
            kw["ROOT_URLCONF"] = "importd.urlconf"
            if "TEMPLATE_DIRS" not in kw:
                kw["TEMPLATE_DIRS"] = (self.dotslash("templates"),)
            if "STATIC_URL" not in kw:
                kw["STATIC_URL"] = "/static/"
            if "STATIC_ROOT" not in kw:
                kw["STATIC_ROOT"] = self.dotslash("static")
            if "MEDIA_URL" not in kw:
                kw["MEDIA_URL"] = "/static/media/"
            if "db" in kw:
                if isinstance(kw["db"], basestring):
                    kw["DATABASES"] = {
                        "default": dj_database_url.parse(kw.pop("db"))
                    }
                else:
                    db = kw.pop("db")
                    default = dj_database_url.parse(db[0])
                    default.update(db[1])
                    kw["DATABASES"] = dict(default=default)
            if "DATABASES" not in kw:
                kw["DATABASES"] = {
                    "default": {
                        'ENGINE': "django.db.backends.sqlite3",
                        'NAME': self.dotslash("db.sqlite3")
                    }
                }

            self.smart_return = False
            if kw.pop("SMART_RETURN", True):
                self.smart_return = True
                kw.setdefault(
                    'MIDDLEWARE_CLASSES',
                    list(global_settings.MIDDLEWARE_CLASSES)
                ).insert(0, "importd.SmartReturnMiddleware")

            installed = list(kw.setdefault("INSTALLED_APPS", []))

            admin_url = kw.pop("admin", "^admin/")

            if admin_url:
                if "django.contrib.auth" not in installed:
                    installed.append("django.contrib.auth")
                if "django.contrib.contenttypes" not in installed:
                    installed.append("django.contrib.contenttypes")
                if "django.contrib.auth" not in installed:
                    installed.append("django.contrib.auth")
                if "django.contrib.messages" not in installed:
                    installed.append("django.contrib.messages")
                if "django.contrib.sessions" not in installed:
                    installed.append("django.contrib.sessions")
                if "django.contrib.admin" not in installed:
                    installed.append("django.contrib.admin")
                if "django.contrib.humanize" not in installed:
                    installed.append("django.contrib.humanize")
                if "django.contrib.staticfiles" not in installed:
                    installed.append("django.contrib.staticfiles")
                if "debug_toolbar" not in installed and DEBUG_TOOLBAR:
                    installed.append("debug_toolbar")
                    kw['INTERNAL_IPS'] = ('127.0.0.1', '0.0.0.0')
                    kw['MIDDLEWARE_CLASSES'].insert(
                        1, 'debug_toolbar.middleware.DebugToolbarMiddleware')
                    kw['DEBUG_TOOLBAR_CONFIG'] = {
                        'SHOW_TOOLBAR_CALLBACK': lambda v: 1 == 1,
                        'INTERCEPT_REDIRECTS': False}
                    kw['DEBUG_TOOLBAR_PANELS'] = (
                    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
                        'debug_toolbar.panels.version.VersionDebugPanel',
                        'debug_toolbar.panels.timer.TimerDebugPanel',
                        'debug_toolbar.panels.headers.HeaderDebugPanel',
                        'debug_toolbar.panels.profiling.ProfilingDebugPanel',
                        'debug_toolbar.panels.sql.SQLDebugPanel',
                        'debug_toolbar.panels.template.TemplateDebugPanel',
                        'debug_toolbar.panels.cache.CacheDebugPanel',
                        'debug_toolbar.panels.signals.SignalDebugPanel',
                        'debug_toolbar.panels.logger.LoggingPanel')
                    # This one gives 500 if its Enabled without previous syncdb
                    #'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',

            kw['INSTALLED_APPS'] = installed

            if "DEBUG" not in kw:
                kw["DEBUG"] = kw["TEMPLATE_DEBUG"] = True
            if "APP_DIR" not in kw:
                kw["APP_DIR"] = self.APP_DIR
            if "SECRET_KEY" not in kw:
                kw["SECRET_KEY"] = self.get_secret_key()
            # admins and managers
            if "ADMINS" not in kw:
                kw["ADMINS"] = kw["MANAGERS"] = ((getuser(), ""), )
            settings.configure(**kw)
            self._import_django()

            # import .views and .forms for each installed app
            for app in settings.INSTALLED_APPS:
                try:
                    __import__("{}.views".format(app))  # lint:ok
                except ImportError:
                    pass
                try:
                    __import__("{}.forms".format(app))  # lint:ok
                except ImportError:
                    pass
                try:
                    __import__("{}.signals".format(app))  # lint:ok
                except ImportError:
                    pass

            self.urlpatterns += staticfiles_urlpatterns()

            if admin_url:
                admin.autodiscover()
                self.add_view(admin_url, include(admin.site.urls))

        self._configured = True

    def __call__(self, *args, **kw):
        if args:
            if not hasattr(self, "_configured"):
                self._configure_django(DEBUG=True)
            if type(args[0]) == dict and len(args) == 2:
                return self.wsgi_application(*args)
            if self._is_management_command(args[0]):
                self._handle_management_command(*args, **kw)
                return self
            if type(args[0]) == list:
                self.update_urls(args[0])
                return self
            if callable(args[0]):
                self.add_view("/{}/".format(args[0].__name__), args[0])
                return args[0]

            def ddecorator(candidate):

                # the following is unsafe
                if type(candidate) == forms.DeclarativeFieldsMetaclass:
                    self.add_form(args[0], candidate, *args[1:], **kw)
                    return candidate
                self.add_view(args[0], candidate, *args[1:], **kw)
                return candidate
            return ddecorator
        else:
            self._configure_django(**kw)
        return self

    def _act_as_manage(self, *args):
        if not hasattr(self, "_configured"):
            self._configure_django(DEBUG=True)
        from django.core import management
        management.execute_from_command_line([sys.argv[0]] + list(args))

    def main(self):
        if len(sys.argv) == 1:
            self.do("runserver")
        else:
            self.do()

    def do(self, *args):
        if not args:
            args = sys.argv[1:]
        if len(args) == 0:
            return self._handle_management_command("runserver", "8000")

        return self._act_as_manage(*args)


###############################################################################


application = d = D()
