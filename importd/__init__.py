import sys, os, inspect
try:
    import importlib
except ImportError:
    from django.utils import importlib

import django.core.urlresolvers
from importd import urlconf

if sys.version_info >= (3,):
    basestring = unicode = str

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
            from django.http import HttpResponse as RBase

        from fhurl import JSONResponse
        res = view_func(request, *view_args, **view_kwargs)
        if isinstance(res, basestring):
            res = res, {}
        if isinstance(res, RBase): return res
        if isinstance(res, tuple):
            template_name, context = res
            res = render_to_response(
                template_name, context, RequestContext(request)
            )
        else:
            res = JSONResponse(res)
        return res

class D(object):
    urlpatterns = urlconf.urlpatterns

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
        self.urlpatterns += urls

    # tuple list of django modules imported in d
    # tuple (a, b) is equivalent to from a import b
    # if b is an iterable (b = [c, d]), it is equivalent 
    # to from a import c, d
    DJANGO_IMPORT = (
        ('smarturls', 'surl'),
        ('django.http', ['HttpResponse', 'Http404', 'HttpResponseRedirect']),
        ('django.shortcuts', ['get_object_or_404', 'render_to_response']),
        ('django.conf.urls.defaults', ['patterns', 'url']),
        ('django.template', 'RequestContext'),
        ('django', 'forms'),
        ('fhurl', ['RequestForm', 'fhurl', 'JSONResponse']),
        ('django.db.models', ''),
    )

    def _iterate_imports(self, callback):
        """Iterates through imports and calls callback for each
        (module_name, attributes) pair. If attribute is a string, it is 
        converted to a list first. Empty strings become empty lists"""

        for module_name, attributes in self.DJANGO_IMPORT:
            if isinstance(attributes, basestring):
                if attributes:
                    attributes = [attributes]
                else:
                    attributes = []
            callback(module_name, attributes)  # check if its a decorated view from importd

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
            from django.core.wsgi import get_wsgi_application
            self.wsgi_application = get_wsgi_application()
        except ImportError:
            import django.core.handlers.wsgi
            self.wsgi_application = django.core.handlers.wsgi.WSGIHandler()

    def dotslash(self, pth):
        return os.path.join(self.APP_DIR, pth)

    def generate_mount_url(self, regex, v_or_f, mod):
        # self.mounts can be None, which means no url generation,
        # url is being managed by urlpatterns.
        # else self.mounts is a dict, containing app name and where to mount
        # if where it mount is None then again dont mount this fellow
        if self.mounts is None: return # we dont want to mount anything
        if not regex.startswith("/"): return regex

        if not mod:
            if isinstance(v_or_f, basestring):
                mod = v_or_f
            else: # if hasattr(v_or_f, "__module__")?
                mod = v_or_f.__module__

        best_k, best_v = "", None

        for k, v in self.mounts.items():
            if mod.startswith(k) and len(k) > len(best_k):
                best_k = k
                best_v = v

        if best_k:
            if not best_v: return
            if not best_v.endswith("/"): best_k += "/"
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

    def _configure_django(self, **kw):
        from django.conf import settings, global_settings
        self.settings = settings
        if settings.configured: return

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
                kw["STATIC_URL"] = "static/"
            if "STATICFILES_DIRS" not in kw:
                kw["STATICFILES_DIRS"] = (self.dotslash("static"),)
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

            kw['INSTALLED_APPS'] = installed

            if "DEBUG" not in kw: kw["DEBUG"] = True
            if "APP_DIR" not in kw: kw["APP_DIR"] = self.APP_DIR

            settings.configure(**kw)
            self._import_django()

            # import .views and .forms for each installed app
            for app in settings.INSTALLED_APPS:
                try:
                    __import__("%s.views" % app)
                except ImportError:
                    pass
                try:
                    __import__("%s.forms" % app)
                except ImportError:
                    pass
                try:
                    __import__("%s.signals" % app)
                except ImportError:
                    pass

            from django.contrib.staticfiles.urls import staticfiles_urlpatterns
            self.urlpatterns += staticfiles_urlpatterns()

            if admin_url:
                from django.contrib import admin
                try:
                    from django.conf.urls import include
                except ImportError:
                    from django.conf.urls.defaults import include
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
                self.add_view("/%s/" % args[0].__name__, args[0])
                return args[0]
            def ddecorator(candidate):
                from django.forms import forms
                if type(candidate) == forms.DeclarativeFieldsMetaclass:  # unsafe
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
        if not args: args = sys.argv[1:]
        if len(args) == 0:
            return self._handle_management_command("runserver", "8000")

        return self._act_as_manage(*args)

application = d = D()
