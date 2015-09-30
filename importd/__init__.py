# -*- coding: utf-8 -*-


"""ImportD django mini framework."""


__version__ = "0.4.1"
__license__ = "BSD"
__author__ = "Amit Upadhyay"
__email__ = "upadhyay@gmail.com"
__url__ = "http://amitu.com/importd"
__source__ = "https://github.com/amitu/importd"
__docformat__ = "html"


# stdlib imports
import copy
import inspect
import os
import sys
import traceback
from datetime import datetime
from getpass import getuser
from platform import python_version

# 3rd party imports
import dj_database_url
import django.core.urlresolvers
import django
from importd import urlconf  # noqa lint:ok
from django.conf import settings
from collections import Callable

# custom imports
try:
    import importlib
except ImportError:
    from django.utils import importlib  # lint:ok
try:
    import debug_toolbar  # lint:ok
except ImportError:
    debug_toolbar = None
try:
    import werkzeug  # lint:ok
    import django_extensions  # lint:ok
except ImportError:
    django_extensions = werkzeug = None
try:
    import django_jinja  # noqa lint:ok
    DJANGO_JINJA = True
except ImportError:
    DJANGO_JINJA = False
try:
    import coffin  # noqa lint:ok
    COFFIN = True
except ImportError:
    COFFIN = False
try:
    import resource
except ImportError:
    resource = None

from path import path

start_time = datetime.now()
if python_version().startswith('3'):
    basestring = unicode = str  # noqa lint:ok
    # coffin is not python 3 compatible library
    COFFIN = False

# cannot use django-jinja, coffin both. primary library is coffin.
if COFFIN and DJANGO_JINJA:
    DJANGO_JINJA = False


##############################################################################


class SmartReturnMiddleware(object):

    """
    Smart response middleware for views.

    Converts view return to the following:
    HttpResponse - stays the same
    string - renders the template named in the string
    (string, dict) - renders the template with keyword arguments.
    object - renders JSONResponse of the object
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Take request and view function and process with arguments."""
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
            res = render_to_response(template_name, context,
                                     RequestContext(request))
        else:
            res = JSONResponse(res)
        return res


class Blueprint(object):

    """
    Blueprint is way to group urls.

    This class is used for save blueprint info.
    The instance of blueprint class is used inside D object initialization.
    """

    def __init__(self):
        """Init class."""
        self.url_prefix, self.namespace, self.app_name = None, None, None

        from django.conf.urls import patterns
        self.patterns = patterns('')

        from smarturls import surl
        self.surl = surl

        from fhurl import fhurl
        self.fhurl = fhurl

    def add_view(self, regex, view, app=None, *args, **kw):
        """Take a regular expression and add a view to the app patterns."""
        url = self.surl(regex, view, *args, **kw)
        self.patterns.append(url)

    def add_form(self, regex, form_cls, app=None, *args, **kw):
        """Take a regular expression and add a form to the app patterns."""
        url = self.fhurl(regex, form_cls, *args, **kw)
        self.patterns.append(url)

    def __call__(self, *args, **kw):
        """Call the class instance."""
        if isinstance(args[0], Callable):
            self.add_view("/{}/".format(args[0].__name__), args[0])
            return args[0]

        def ddecorator(candidate):
            from django.forms import forms  # the following is unsafe
            if isinstance(candidate, forms.DeclarativeFieldsMetaclass):
                self.add_form(args[0], candidate, *args[1:], **kw)
                return candidate
            self.add_view(args[0], candidate, *args[1:], **kw)
            return candidate

        return ddecorator


NotSet = object()
RaiseException = object()


def env(key, default="", factory=None):
    # default=RaiseException is a way to force an environment variable to be
    # present else django fails to start.
    if default is RaiseException and key not in os.environ:
        raise KeyError(key)

    val = os.environ.get(key, default)

    # why are we calling strip? envdir lets you store env variables in files,
    # which is good but editors tend to insert extra new line at end of file,
    # and it usually never makes sense for a environment variable to have a
    # trailing new line.
    if isinstance(val, basestring):
        val = val.strip()

    # if default value is NotSet and factory is set, we do not want to invoke
    # factory on value as factory probably only takes string
    if val == default == NotSet:
        return NotSet

    # if factory is set to NotSet, developer is trying to bypass whole factory
    # handling
    if factory != NotSet:
        # if no factory is set, we can get factory from default value
        if not factory and default != NotSet:
            factory = type(default)

        # if default value is not known, and factory was not specified(==None),
        # we will not have a value for factory function.
        if factory:
            if factory == bool:
                if isinstance(val, basestring) and val.lower() in [
                    "no", "false", "off", "0"
                ]:
                    val = False
            val = factory(val)

    return val


class DSetting(object):
    """
    Some settings can have different value depending on if they are for debug
    or in prod environment.

    importd supports configuring those setting variables via importd.debug()
    function such that debug stuff goes in debug environment and prod in prod.
    """
    def __init__(self, dvalue=NotSet, prod=NotSet):
        self.dvalue = dvalue
        self.pvalue = prod

debug = DSetting


class E(object):
    """
    importd supports a feature that allows you to selectively export things
    from settings file to be available to templates. We have a context
    preprocessor that adds whole settings to template contexts, but some teams
    find it too open, as very sensitive data is stored in settings. Also this
    makes it harder to justify a debug_settings that shows all settings
    variables in template for temporary debug purpose.

    The solution is to mark settings that you want to be exposed to templates
    using the e() function in importd, which attaches all "exposed" settings to
    a variable named esettings when using a context preprocessor
    importd.esettings.

    This class is used for that.
    """
    def __init__(self, value):
        self.value = value


e = E


class ESettings(object):
    pass


global_esettings = ESettings()


def esettings(request):
    return {
        "esettings": global_esettings
    }


##############################################################################


class D(object):

    """D Main Class."""

    def __init__(self):
        """Init class."""
        self.blueprint_list = []

    @property
    def urlpatterns(self):
        """Return the regex patterns."""
        return self.get_urlpatterns()

    def _is_management_command(self, cmd):
        """Take a string argument and return boolean of its a command."""
        return cmd in ("runserver", "shell")

    def _handle_management_command(self, cmd, *args, **kw):
        """Take command and arguments and call them using Django."""
        if not hasattr(self, "_configured"):
            self._configure_django(DEBUG=True)
        from django.core import management
        management.call_command(cmd, *args, **kw)

    def update_regexers(self, regexers):
        """Update regular expressions."""
        self.regexers.update(regexers)

    def update_urls(self, urls):
        """Update regular urls."""
        urlpatterns = self.get_urlpatterns()
        urlpatterns += urls

    def get_urlpatterns(self):
        """Return url patterns."""
        urlconf_module = importlib.import_module(settings.ROOT_URLCONF)
        return urlconf_module.urlpatterns

    def _import_django(self):
        """Do the Django imports."""
        from smarturls import surl  # issue #19. manual imports
        self.surl = surl

        from django.http import HttpResponse, Http404, HttpResponseRedirect
        self.HttpResponse = HttpResponse
        self.Http404, self.HttpResponseRedirect = Http404, HttpResponseRedirect

        from django.shortcuts import (get_object_or_404, get_list_or_404,
                                      render_to_response, render, redirect)
        self.get_object_or_404 = get_object_or_404
        self.get_list_or_404 = get_list_or_404
        self.render_to_response = render_to_response
        self.render, self.redirect = render, redirect

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
            # https://devcenter.heroku.com/articles/django-assets
            from whitenoise.django import DjangoWhiteNoise
            self.wsgi_application = DjangoWhiteNoise(self.wsgi_application)
        except ImportError:
            pass

        try:
            from django.conf.urls.defaults import patterns, url
        except ImportError:
            from django.conf.urls import patterns, url  # lint:ok
        self.patterns, self.url = patterns, url

    def _get_app_dir(self, pth):
        """Return the path of the app."""
        return path(os.path.join(self.APP_DIR, pth))

    def dotslash(self, pth):
        """Mimic the unix './' behaviour."""
        if hasattr(self, "APP_DIR"):
            return self._get_app_dir(pth=pth)
        else:
            try:
                import speaklater
            except ImportError:
                raise RuntimeError("Configure django, or install speaklater.")
            else:
                return speaklater.make_lazy_string(self._get_app_dir, pth)

    def generate_mount_url(self, regex, v_or_f, mod):
        """The self.mounts can be None, which means no url generation.

        url is being managed by urlpatterns.
        else self.mounts is a dict, containing app name and where to mount
        if where it mount is None then again don't mount this fellow.
        """
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

        for k, v in tuple(self.mounts.items()):
            if mod.startswith(k) and len(k) > len(best_k):
                best_k, best_v = k, v

        if best_k:
            if not best_v:
                return
            if not best_v.endswith("/"):
                best_k += "/"
            if best_v != "/":
                regex = best_v[:-1] + regex

        return regex

    def add_view(self, regex, view, app=None, *args, **kw):
        """Take a view and add it to the app using regex arguments."""
        regex = self.generate_mount_url(regex, view, app)
        if regex:
            patterns = self.patterns("", self.surl(regex, view, *args, **kw))
            urlpatterns = self.get_urlpatterns()
            urlpatterns += patterns
            django.core.urlresolvers.clear_url_caches()

    def add_form(self, regex, form_cls, app=None, *args, **kw):
        """Take a form and add it to the app using regex arguments."""
        regex = self.generate_mount_url(regex, form_cls, app)
        if regex:
            urlpatterns = self.get_urlpatterns()
            urlpatterns.append(self.fhurl(regex, form_cls, *args, **kw))
            django.core.urlresolvers.clear_url_caches()

    def get_secret_key(self):
        """Get a django secret key,try to read provided one,or generate it."""
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

    def _fix_coffin_pre(self):
        try:
            from django.template import add_to_builtins
        except ImportError:
            from django.template.base import (
                add_to_builtins, import_library, Origin,
                InvalidTemplateLibrary, builtins, get_library)
            import django.template
            django.template.add_to_builtins = add_to_builtins
            django.template.import_library = import_library
            django.template.Origin = Origin
            django.template.InvalidTemplateLibrary = InvalidTemplateLibrary
            django.template.builtins = builtins
            django.template.get_library = get_library

    def _fix_coffin_post(self):
        try:
            from django.template.loaders.app_directories import (
                app_template_dirs)
        except ImportError:
            from django.template.utils import get_app_template_dirs
            import django.template.loaders.app_directories
            django.template.loaders.app_directories.app_template_dirs = (
                get_app_template_dirs('templates')
            )
        else:
            app_template_dirs = app_template_dirs

    def _configure_django(self, **kw):
        """Auto-Configure Django using arguments."""
        from django.conf import settings, global_settings
        self.settings = settings
        if settings.configured:
            return

        self.APP_DIR, app_filename = os.path.split(
            os.path.realpath(inspect.stack()[2][1])
        )

        DEBUG = kw.get("DEBUG", False)
        md = {}
        dp = {}

        for k, v in kw.items():
            if isinstance(v, E):
                md[k] = v.value
                setattr(global_esettings, k, v.value)
            if isinstance(v, DSetting):
                dp[k] = v

        for k, v in md.items():
            kw[k] = v

        for k, v in dp.items():
            if DEBUG:
                if v.dvalue is not NotSet:
                    kw[k] = v.dvalue
            else:
                if v.pvalue is not NotSet:
                    kw[k] = v.pvalue

        del md
        del dp

        def do_dp(key):
            if key not in kw:
                return
            old = kw[key]
            kw[key] = []
            for value in old:
                if DEBUG:
                    if value.startswith("prod:"):
                        continue
                    kw[key].append(value.replace("debug:", ""))
                else:
                    if value.startswith("debug:"):
                        continue
                    kw[key].append(value.replace("prod:", ""))

        do_dp("MIDDLEWARE_CLASSES")
        do_dp("INSTALLED_APPS")
        do_dp("TEMPLATE_CONTEXT_PROCESSORS")

        if "debug" in kw:
            db = kw.pop("debug")
            if DEBUG:
                kw.update(db)

        if "regexers" in kw:
            self.update_regexers(kw.pop("regexers"))

        self.mounts = kw.pop("mounts", {})

        if not kw.get("dont_configure", False):
            kw["ROOT_URLCONF"] = kw.get("ROOT_URLCONF", "importd.urlconf")
            if "TEMPLATE_DIRS" not in kw:
                kw["TEMPLATE_DIRS"] = (self.dotslash("templates"), )
            if "STATIC_URL" not in kw:
                kw["STATIC_URL"] = "/static/"
            if "STATIC_ROOT" not in kw:
                kw["STATIC_ROOT"] = self.dotslash("staticfiles")
            if "STATICFILES_DIRS" not in kw:
                kw["STATICFILES_DIRS"] = [self.dotslash("static")]
            if "MEDIA_URL" not in kw:
                kw["MEDIA_URL"] = "/static/media/"
            if "lr" in kw:
                self.lr = kw.pop("lr")
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
                    # check session middleware installed
                    # https://docs.djangoproject.com/en/1.7/topics/http/sessions/#enabling-sessions
                    last_position = len(kw["MIDDLEWARE_CLASSES"])
                    kw["MIDDLEWARE_CLASSES"] = list(kw["MIDDLEWARE_CLASSES"])
                    kw["MIDDLEWARE_CLASSES"].insert(
                        last_position,
                        "django.contrib.sessions.middleware.SessionMiddleware"
                    )
                if "django.contrib.admin" not in installed:
                    installed.append("django.contrib.admin")
                    kw["MIDDLEWARE_CLASSES"].append(
                        "django.contrib.auth.middleware"
                        ".AuthenticationMiddleware"
                    )
                if "django.contrib.humanize" not in installed:
                    installed.append("django.contrib.humanize")
                if "django.contrib.staticfiles" not in installed:
                    installed.append("django.contrib.staticfiles")
                if "debug_toolbar" not in installed and debug_toolbar:
                    installed.append("debug_toolbar")
                    if 'INTERNAL_IPS' not in kw:
                        kw['INTERNAL_IPS'] = ('127.0.0.1', '0.0.0.0')
                    kw['MIDDLEWARE_CLASSES'].insert(
                        1,
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
                    # 'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',

            if django_extensions and werkzeug:
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
                kw["DEBUG"] = kw["TEMPLATE_DEBUG"] = True
            if "APP_DIR" not in kw:
                kw["APP_DIR"] = self.APP_DIR
            if "SECRET_KEY" not in kw:
                kw["SECRET_KEY"] = self.get_secret_key()
            # admins and managers
            if "ADMINS" not in kw:
                kw["ADMINS"] = kw["MANAGERS"] = ((getuser(), ""), )
            autoimport = kw.pop("autoimport", True)

            kw["SETTINGS_MODULE"] = kw.get("SETTINGS_MODULE", "importd")

            # self._fix_coffin_pre()
            settings.configure(**kw)
            if hasattr(django, "setup"):
                django.setup()

            self._import_django()
            # self._fix_coffin_post()

            from django.contrib.staticfiles.urls import staticfiles_urlpatterns
            urlpatterns = self.get_urlpatterns()
            urlpatterns += staticfiles_urlpatterns()

            if autoimport:
                # django depends on INSTALLED_APPS's model
                for app in settings.INSTALLED_APPS:
                    self._import_app_module("{}.admin", app)
                    self._import_app_module("{}.models", app)

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
                    self._import_app_module("{}.forms", app)
                    self._import_app_module("{}.views", app)
                    self._import_app_module("{}.signals", app)

        # import blueprints from config
        self.blueprints = kw.pop("blueprints", {})
        for namespace, meta in self.blueprints.items():
            if isinstance(meta, basestring):
                meta = {"blueprint": meta}

            mod_path, bp_name = meta["blueprint"].rsplit(".", 1)
            mod = importlib.import_module(mod_path)
            bp = getattr(mod, bp_name)

            self.register_blueprint(
                bp, url_prefix=meta.get("url_prefix", namespace + "/"),
                namespace=namespace, app_name=meta.get("app_name", ""))

        self._configured = True

    def _import_app_module(self, fmt, app):
        """Try to import an app module."""
        try:
            __import__(fmt.format(app))  # lint:ok
        except ImportError:
            pass
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            raise SystemExit(-1)

    def __call__(self, *args, **kw):
        """Call instance class."""
        if args:
            if not hasattr(self, "_configured"):
                self._configure_django(DEBUG=True)
            if isinstance(args[0], dict) and len(args) == 2:
                for bp in self.blueprint_list:
                    self.apply_blueprint(bp)
                return self.wsgi_application(*args)
            if self._is_management_command(args[0]):
                self._handle_management_command(*args, **kw)
                return self
            if isinstance(args[0], list):
                self.update_urls(args[0])
                return self
            if isinstance(args[0], Callable):
                self.add_view("/{}/".format(args[0].__name__), args[0])
                return args[0]

            def ddecorator(candidate):
                from django.forms import forms
                # the following is unsafe
                if isinstance(candidate, forms.DeclarativeFieldsMetaclass):
                    self.add_form(args[0], candidate, *args[1:], **kw)
                    return candidate
                self.add_view(args[0], candidate, *args[1:], **kw)
                return candidate
            return ddecorator
        else:
            self._configure_django(**kw)
        return self

    def _act_as_manage(self, *args):
        """Mimic Djangos manage.py."""
        if not hasattr(self, "_configured"):
            self._configure_django(DEBUG=True)
        from django.core import management
        management.execute_from_command_line([sys.argv[0]] + list(args))

    def register_blueprint(self, bp, url_prefix, namespace, app_name=''):
        """
        Interface to register blueprint.

        See django url namespace.
        https://docs.djangoproject.com/en/1.7/topics/http/urls/#url-namespaces
        """
        clone_bp = copy.deepcopy(bp)
        clone_bp.url_prefix = url_prefix
        clone_bp.namespace = namespace
        clone_bp.app_name = app_name
        self.blueprint_list.append(clone_bp)

    def _apply_blueprint(self, bp):
        """Apply a Blueprint."""
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
        """Wrapper for calling do."""
        if len(sys.argv) == 1:
            self.do(self._get_runserver_cmd())
        else:
            self.do()

    def do(self, *args):
        """Run Django with ImportD."""
        for bp in self.blueprint_list:
            self._apply_blueprint(bp)

        if not args:
            args = sys.argv[1:]

        if len(args) == 0:
            return self._handle_management_command(
                self._get_runserver_cmd(), "8000")

        if 'livereload' in sys.argv:
            if not hasattr(self, "lr"):
                print("Livereload setting, lr not configured.")
                return
            from livereload import Server
            server = Server(self)
            for pat, cmd in self.lr.items():
                parts = pat.split(",")
                for part in parts:
                    server.watch(part, cmd)
            server.serve(port=8000)
            return

        return self._act_as_manage(*args)

    def _get_runserver_cmd(self):
        """Return a proper runserver command."""
        return 'runserver_plus' if django_extensions else 'runserver'


application = d = D()
