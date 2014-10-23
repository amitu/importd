# -*- coding: utf-8 -*-
# isort:skip_file


# stdlib imports
import inspect
import os
import sys

# 3rd party imports
import dj_database_url
import django.core.urlresolvers
from importd import urlconf
from django.conf import settings

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
    import werkzeug
    import django_extensions
    RUNSERVER_PLUS = True
except ImportError:
    RUNSERVER_PLUS = False
try:
    import django_jinja  # lint:ok
    DJANGO_JINJA = True
except ImportError:
    DJANGO_JINJA = False
try:
    import coffin  # lint:ok
    COFFIN = True
except ImportError:
    COFFIN = False


if sys.version_info >= (3,):
    basestring = unicode = str  # lint:ok
    # coffin is not python 3 compatible library
    COFFIN = False

# cannot use django-jinja, coffin both. primary library is coffin.
if COFFIN and DJANGO_JINJA:
    DJANGO_JINJA = False


class SmartReturnMiddleware(object):
    """
    Smart response middleware for views. Converts view return to the following:
    HttpResponse - stays the same
    string - renders the template named in the string
    (string, dict) - renders the template with keyword arguments.
    object - renders JSONResponse of the object
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        from django.shortcuts import render_to_response
        from django.template import RequestContext
        try:
            from django.http.response import HttpResponseBase as RBase
        except ImportError:
            from django.http import HttpResponse as RBase  # lint:ok

        from fhurl import JSONResponse
        res = view_func(request, *view_args, **view_kwargs)
        if isinstance(res, basestring):
            res = res, {}
        if isinstance(res, RBase):
            return res
        if isinstance(res, tuple):
            template_name, context = res
            res = render_to_response(
                template_name, context, RequestContext(request)
            )
        else:
            res = JSONResponse(res)
        return res

class Blueprint(object):
    def __init__(self):
        self.url_prefix = None
        self.namespace = None
        self.app_name = None

        from django.conf.urls import patterns
        self.patterns = patterns('')

        from smarturls import surl
        self.surl = surl

        from fhurl import fhurl
        self.fhurl = fhurl

    def add_view(self, regex, view, app=None, *args, **kw):
        url = self.surl(regex, view, *args, **kw)
        self.patterns.append(url)

    def add_form(self, regex, form_cls, app=None, *args, **kw):
        url = self.fhurl(regex, form_cls, *args, **kw)
        self.patterns.append(url)

    def __call__(self, *args, **kw):
        if callable(args[0]):
            self.add_view("/{}/".format(args[0].__name__), args[0])
            return args[0]

        def ddecorator(candidate):
            from django.forms import forms
            # the following is unsafe
            if type(candidate) == forms.DeclarativeFieldsMetaclass:
                self.add_form(args[0], candidate, *args[1:], **kw)
                return candidate
            self.add_view(args[0], candidate, *args[1:], **kw)
            return candidate
        return ddecorator



class D(object):
    def __init__(self):
        self.blueprint_list = []

    @property
    def urlpatterns(self):
        return self.get_urlpatterns()

    def _is_management_command(self, cmd):
        return cmd in "runserver,shell".split(",")

    def _handle_management_command(self, cmd, *args, **kw):
        if not hasattr(self, "_configured"):
            self._configure_django(DEBUG=True)
        from django.core import management
        management.call_command(cmd, *args, **kw)

    def update_regexers(self, regexers):
        self.regexers.update(regexers)

    def update_urls(self, urls):
        urlpatterns = self.get_urlpatterns()
        urlpatterns += urls

    def get_urlpatterns(self):
        urlconf_module = importlib.import_module(settings.ROOT_URLCONF)
        return urlconf_module.urlpatterns

    def _import_django(self):
        # issue #19. manual imports
        from smarturls import surl
        self.surl = surl

        from django.http import HttpResponse, Http404, HttpResponseRedirect
        self.HttpResponse = HttpResponse
        self.Http404 = Http404
        self.HttpResponseRedirect = HttpResponseRedirect

        from django.shortcuts import get_object_or_404, get_list_or_404, render_to_response, render, redirect
        self.get_object_or_404 = get_object_or_404
        self.get_list_or_404 = get_list_or_404
        self.render_to_response = render_to_response
        self.render = render
        self.redirect = redirect

        from django.template import RequestContext
        self.RequestContext = RequestContext

        from django import forms
        self.forms = forms

        from fhurl import RequestForm, fhurl, JSONResponse
        self.RequestForm = RequestForm
        self.fhurl = fhurl
        self.JSONResponse = JSONResponse

        try:
            from django.core.wsgi import get_wsgi_application
            self.wsgi_application = get_wsgi_application()
        except ImportError:
            import django.core.handlers.wsgi
            self.wsgi_application = django.core.handlers.wsgi.WSGIHandler()

        try:
            from django.conf.urls.defaults import patterns, url
        except ImportError:
            from django.conf.urls import patterns, url  # lint:ok
        self.patterns = patterns
        self.url = url

    def _get_app_dir(self, pth):
        return os.path.join(self.APP_DIR, pth)

    def dotslash(self, pth):
        if hasattr(self, "APP_DIR"):
            return self._get_app_dir(pth=pth)
        else:
            try:
                import speaklater
            except ImportError:
                raise RuntimeError(
                    "configure django first, or install speaklater"
                )
            else:
                return speaklater.make_lazy_string(
                    self._get_app_dir, pth
                )

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
            patterns = self.patterns(
                "", self.surl(regex, view, *args, **kw)
            )
            urlpatterns = self.get_urlpatterns()
            urlpatterns += patterns
            django.core.urlresolvers.clear_url_caches()

    def add_form(self, regex, form_cls, app=None, *args, **kw):
        regex = self.generate_mount_url(regex, form_cls, app)
        if regex:
            urlpatterns = self.get_urlpatterns()
            urlpatterns.append(self.fhurl(regex, form_cls, *args, **kw))
            django.core.urlresolvers.clear_url_caches()

    def get_secret_key(self):
        """get a django secret key,try to read provided one,else generate it"""
        try:
            with open(self.dotslash("secret.txt"), "r") as f:
                secret = f.readlines()[0].strip()
        except (IOError, IndexError):
            with open(self.dotslash("secret.txt"), "w") as f:
                from string import ascii_letters, digits
                from random import sample
                secret = "".join(sample(ascii_letters + digits, 50))
                f.write(secret)
        finally:
            return secret

    def _configure_django(self, **kw):
        from django.conf import settings, global_settings
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
                kw["STATIC_ROOT"] = self.dotslash("staticfiles")
            if "STATICFILES_DIRS" not in kw:
                kw["STATICFILES_DIRS"] = [self.dotslash("static")]
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
                        'NAME': self.dotslash("db.sqlite")
                    }
                }

            self.smart_return = False
            if kw.pop("SMART_RETURN", True):
                self.smart_return = True
                if "MIDDLEWARE_CLASSES" not in kw:
                    kw["MIDDLEWARE_CLASSES"] = (
                        global_settings.MIDDLEWARE_CLASSES
                    )
                kw["MIDDLEWARE_CLASSES"] = list(kw["MIDDLEWARE_CLASSES"])
                kw["MIDDLEWARE_CLASSES"].insert(
                    0, "importd.SmartReturnMiddleware"
                )

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
                    if 'INTERNAL_IPS' not in kw:
                        kw['INTERNAL_IPS'] = ('127.0.0.1', '0.0.0.0')
                    kw['MIDDLEWARE_CLASSES'].insert(1,
                        'debug_toolbar.middleware.DebugToolbarMiddleware')
                    kw['DEBUG_TOOLBAR_PANELS'] = (
                        'debug_toolbar.panels.versions.VersionsPanel',
                        'debug_toolbar.panels.timer.TimerPanel',
                        'debug_toolbar.panels.settings.SettingsPanel',
                        'debug_toolbar.panels.headers.HeadersPanel',
                        'debug_toolbar.panels.request.RequestPanel',
                        'debug_toolbar.panels.sql.SQLPanel',
                        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
                        'debug_toolbar.panels.templates.TemplatesPanel',
                        'debug_toolbar.panels.cache.CachePanel',
                        'debug_toolbar.panels.signals.SignalsPanel',
                        'debug_toolbar.panels.logging.LoggingPanel',
                        'debug_toolbar.panels.redirects.RedirectsPanel',
                    )
                    # This one gives 500 if its Enabled without previous syncdb
                    #'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',

            if RUNSERVER_PLUS:
                installed.append('django_extensions')

            # django-jinja 1.0.4 support
            if DJANGO_JINJA:
                installed.append("django_jinja")
                kw['TEMPLATE_LOADERS'] = list(kw.get('TEMPLATE_LOADERS', []))
                kw['TEMPLATE_LOADERS'] += (
                    'django_jinja.loaders.AppLoader',
                    'django_jinja.loaders.FileSystemLoader',
                )
            # coffin 0.3.8 support
            if COFFIN:
                installed.append('coffin')
                kw['TEMPLATE_LOADERS'] = list(kw.get('TEMPLATE_LOADERS', []))
                kw['TEMPLATE_LOADERS'] += (
                    'coffin.contrib.loader.AppLoader',
                    'coffin.contrib.loader.FileSystemLoader',
                )

            kw['INSTALLED_APPS'] = installed

            if "DEBUG" not in kw:
                kw["DEBUG"] = True
            if "APP_DIR" not in kw:
                kw["APP_DIR"] = self.APP_DIR
            if "SECRET_KEY" not in kw:
                kw["SECRET_KEY"] = self.get_secret_key()

            autoimport = kw.pop("autoimport", True)

            kw["SETTINGS_MODULE"] = kw.get("SETTINGS_MODULE", "importd")

            settings.configure(**kw)
            self._import_django()

            from django.contrib.staticfiles.urls import staticfiles_urlpatterns
            urlpatterns = self.get_urlpatterns()
            urlpatterns += staticfiles_urlpatterns()

            if autoimport:
                # django depends on INSTALLED_APPS's model
                for app in settings.INSTALLED_APPS:
                    try:
                        __import__("{}.admin".format(app))  # lint:ok
                    except ImportError:
                        pass
                    try:
                        __import__("{}.models".format(app))  # lint:ok
                    except ImportError:
                        pass

            if admin_url:
                from django.contrib import admin
                try:
                    from django.conf.urls import include
                except ImportError:
                    from django.conf.urls.defaults import include  # lint:ok
                admin.autodiscover()
                self.add_view(admin_url, include(admin.site.urls))

            if autoimport:
                # import .views and .forms for each installed app
                for app in settings.INSTALLED_APPS:
                    try:
                        __import__("{}.forms".format(app))  # lint:ok
                    except ImportError:
                        pass
                    try:
                        __import__("{}.views".format(app))  # lint:ok
                    except ImportError:
                        pass
                    try:
                        __import__("{}.signals".format(app))  # lint:ok
                    except ImportError:
                        pass

        self._configured = True

    def __call__(self, *args, **kw):
        if args:
            if not hasattr(self, "_configured"):
                self._configure_django(DEBUG=True)
            if type(args[0]) == dict and len(args) == 2:
                for bp in self.blueprint_list:
                    self.apply_blueprint(bp)
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
                from django.forms import forms
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

    def register_blueprint(self, bp, url_prefix, namespace, app_name=''):
        bp.url_prefix = url_prefix
        bp.namespace = namespace
        bp.app_name = app_name
        self.blueprint_list.append(bp)

    def apply_blueprint(self, bp):
        try:
            from django.conf.urls import include
        except ImportError:
            from django.conf.urls.defaults import include  # lint:ok

        url = self.surl(bp.url_prefix, include(bp.patterns,
                                               namespace=bp.namespace,
                                               app_name=bp.app_name))

        urlpatterns = self.get_urlpatterns()
        urlpatterns.append(url)
        django.core.urlresolvers.clear_url_caches()

    def main(self):
        if len(sys.argv) == 1:
            self.do(self._get_runserver_cmd())
        else:
            self.do()

    def do(self, *args):
        for bp in self.blueprint_list:
            self.apply_blueprint(bp)

        if not args:
            args = sys.argv[1:]
        if len(args) == 0:
            return self._handle_management_command(self._get_runserver_cmd(), "8000")

        return self._act_as_manage(*args)

    def _get_runserver_cmd(self):
        if RUNSERVER_PLUS:
            return 'runserver_plus'
        else:
            return 'runserver'

application = d = D()
