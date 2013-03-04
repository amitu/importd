class SmartReturnMiddleware(object):
    """Smart response middleware for views. Converts view return to the following:
    HttpResponse - stays the same
    string - renders the template named in the string
    (string, dict) - renders the template with keyword arguments.
    object - renders JSONResponse of the object"""

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
    from django.conf.urls import patterns
    urlpatterns = patterns("")

    class ModelHandler(object):

        def __init__(self, d):
            self.d = d

            from django.db.models import base

            class ImportdModelBase(base.ModelBase):
                """Forces Meta.app_name for each model"""

                def __new__(cls, name, bases, attrs):
                    if "Meta" in attrs:
                        setattr(attrs['Meta'], "app_label",
                                self.d.APP_NAME)
                    else:
                        attrs["Meta"] = type("Meta", (),
                                            {"app_label": self.d.APP_NAME})
                    new_cls = super(ImportdModelBase, cls).__new__(cls,
                                                                   name,
                                                                   bases,
                                                                   attrs)
                    if name != "ImportdModel":
                        setattr(self.d.app_models, name.lower(), new_cls)
                    return new_cls

            class ImportdModel(base.Model):
                __metaclass__ = ImportdModelBase

                class Meta:
                    abstract = True

            self.Model = ImportdModel

        def __getattr__(self, name):
            if name.lower() in dir(self.d.app_models):
                return getattr(self.d.app_models, name.lower())
            else:
                return getattr(self.d._models, name)

        def __call__(self, cls):
            if hasattr(cls, "Meta"):
                setattr(cls.Meta, "app_label", self.d.APP_NAME)
            else:
                class Meta:
                    app_label = self.d.APP_NAME
                setattr(cls, "Meta", Meta)

            from django.db.models import base
            model = base.ModelBase(cls.__name__, (base.Model,),
                                   dict(cls.__dict__))
            setattr(d.app_models, cls.__name__, model)

    def _is_management_command(self, cmd):
        return cmd in "runserver,shell".split(",")

    def _handle_management_command(self, cmd, *args, **kw):
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
        ('django.core.wsgi', 'get_wsgi_application'),
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

        # override models.Models so there metaclass magic isn't called

    def _import_django(self):
        def set_attr(module_name, attributes):
            import importlib
            module = importlib.import_module(module_name)
            if attributes:
                for attribute in attributes:
                    setattr(self, attribute, getattr(module, attribute))
            else:
                setattr(self, module_name.split(".")[-1], module)
        self._iterate_imports(set_attr)
        self._models = self.models
        self.models = self.ModelHandler(self)

        try:
            from django.core.wsgi import get_wsgi_application
            self.wsgi_application = self.get_wsgi_application()
        except ImportError:
            import django.core.handlers.wsgi
            self.wsgi_application = django.core.handlers.wsgi.WSGIHandler()

    def dotslash(self, pth):
        import os
        return os.path.join(self.APP_DIR, pth)

    def register_admin(self, mdl, adm=None):
        from django.contrib import admin
        from django.contrib.admin.sites import AlreadyRegistered
        if adm == None: adm = admin.ModelAdmin
        try:
            admin.site.register(mdl, adm)
        except AlreadyRegistered:
            pass

    def add_view(self, regex, view, *args, **kw):
        self.urlpatterns += self.patterns(
            "", self.surl(regex, view, *args, **kw)
        )
        import django.core.urlresolvers
        django.core.urlresolvers.clear_url_caches()

    def add_form(self, regex, form_cls, *args, **kw):
        self.urlpatterns.append(self.fhurl(regex, form_cls, *args, **kw))

    def _configure_django(self, **kw):
        from django.conf import settings, global_settings
        self.settings = settings
        if settings.configured: return
        
        import inspect, os
        self.APP_DIR, app_filename = os.path.split(
            os.path.realpath(inspect.stack()[2][1])
        )
        self.APP_NAME = app_filename.partition(".")[0] + "_app"

        if "regexers" in kw:
            self.update_regexers(kw.pop("regexers"))


        if not kw.get("dont_configure", False):
            kw["ROOT_URLCONF"] = "importd.d"
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
                kw.setdefault('MIDDLEWARE_CLASSES',
                              list(global_settings.MIDDLEWARE_CLASSES)).\
                              insert(0, "importd.SmartReturnMiddleware")

            # we mock an app, so django internal model loading magic finds
            # the models
            class ModelsMock(object):
                __name__ = self.APP_NAME + ".models"
                __file__ = os.path.join(self.APP_DIR, self.APP_NAME + ".py")
            self.app_models = ModelsMock()

            class AppMock(object):
                __file__ = os.path.join(self.APP_DIR, self.APP_NAME + ".py")
                __name__ = self.APP_NAME
                models = self.app_models

            sys.modules[self.APP_NAME] = AppMock()
            sys.modules[self.APP_NAME + '.models'] = self.app_models

            installed = list(kw.setdefault("INSTALLED_APPS", []))
            installed.append(self.APP_NAME)

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
                except ImportError, e:
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
                from django.conf.urls import include
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
                self.add_view("^%s/$" % args[0].__name__, args[0])
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
        from django.core import management
        import sys
        management.execute_from_command_line([sys.argv[0]] + list(args))

    def main(self):
        import sys
        if len(sys.argv) == 1:
            self.do("runserver")
        elif sys.argv[1] == "convert":
            if len(sys.argv) > 2:
                self.convert(sys.argv[2])
            else:
                self.convert()
        else:
            self.do()

    def do(self, *args):
        import sys
        if not args: args = sys.argv[1:]
        if len(args) == 0:
            return self._handle_management_command("runserver", "8000")

        return self._act_as_manage(*args)

    def _get_view_source(self, view):
        """Takes a view from d.urlpatterns and returns the source of the original
        view without the decorator"""
        import inspect
        source_lines = inspect.getsourcelines(view)[0]

        if source_lines[0].startswith("@d"):
            del source_lines[0]
        return "".join(source_lines)

    def _create_views(self):
        import re
        views = []

        for urlpattern in self.urlpatterns:
            if urlpattern.callback.__module__ == "__main__":
                views.append(self._get_view_source(urlpattern.callback))

        used_imports = set()
        parsed_views = []
        for view in views:
            dobject_regex = re.compile(r'd\.([a-zA-Z]+)')
            used_imports.update(dobject_regex.findall(view))
            parsed_views.append(dobject_regex.sub(lambda m: m.group(1), view))

        imports = []

        imports = []
        def create_import_strings(module_name, attributes):
            if attributes:
                to_import = used_imports.intersection(attributes)
                if to_import:
                    imports.append("from {} import {}".format(
                                                        module_name,
                                                        ", ".join(to_import)))
            else:
                if module_name.split(".")[-1] in used_imports:
                    # special case for models
                    imports.append("from {} import {}".format(
                                        "{}".format(self.APP_NAME),
                                            module_name.split(".")[-1]))
        self._iterate_imports(create_import_strings)
        return "{}\n\n\n{}".format("\n".join(imports), "\n\n".join(parsed_views))

    def _create_urls(self):
        patterns = []
        for pattern in self.urlpatterns:
            func_module = pattern.callback.__module__
            if func_module == '__main__':
                func_module = self.APP_NAME + ".views"
            patterns.append("""(r'{}', '{}.{}')""".format(pattern.regex.pattern,
                                                     func_module,
                                                     pattern.callback.__name__,
                                                     ))
        return """from django.conf.urls import patterns

urlpatterns = patterns("",
            {}
            )
            """.format((",\n" + " " * 12).join(patterns))

    def _create_settings(self):
        import os
        import re
        from pprint import pformat
        from django.conf import settings as django_settings
        settings = {setting for setting in dir(django_settings) \
            if not setting.startswith("_") and re.match(r'[A-Z_]+', setting)}
        settings_lines = []
        for setting in settings:

            if not hasattr(django_settings.default_settings, setting) or\
                    getattr(django_settings, setting) != \
                    getattr(django_settings.default_settings, setting):

                if setting == "ROOT_URLCONF":
                    setting_value = 'urls'
                elif setting == 'MIDDLEWARE_CLASSES':
                    setting_value = []
                    for middleware in getattr(django_settings, setting):
                        setting_value.append(middleware.replace('importd.d', "{}.middleware".format(self.APP_NAME)))
                elif setting == "DATABASES":
                    setting_value = getattr(django_settings, "DATABASES")
                    db_dir, db_name = os.path.split(setting_value['default']['NAME'])
                    setting_value['default']['NAME'] = os.path.join(db_dir, self.APP_NAME.replace("app", "project"),
                                                                    db_name)
                else:
                    setting_value = getattr(django_settings, setting)

                settings_lines.append('{} = {}'.format(setting, pformat(setting_value)))
        return "\n\n".join(settings_lines)

    def _create_middleware(self):
        import inspect
        source_lines = inspect.getsourcelines(self.SmartReturnMiddleware)
        stripped_lines = []
        for line in source_lines[0]:
            stripped_lines.append(line[4:])
        return "".join(stripped_lines)

    def _create_models(self):
        import inspect
        models = []
        for attr in dir(self.app_models):
            model_candidate = getattr(self.app_models, attr)
            if isinstance(model_candidate, type) and\
                issubclass(model_candidate, self.models.Model):

                model_source = inspect.getsource(model_candidate).replace(
                                                        "d.models", "models")
                models.append(model_source)

        return """from django.db import models


{}""".format("\n\n".join(models))

    def _create_manage(self):
        # TODO: look up django-admin.py with shutils and just copy, maybe?
        return """#!/usr/bin/env python
from django.core import management

import settings

if __name__ == "__main__":
    management.execute_manager(settings)
"""

    def _copy_and_replace(self, src, dest):
        """Copies files from src to dest, replaces conflicts.
        From http://stackoverflow.com/questions/7419665/python-move-and-overwrite-files-and-folders (Ray Vega)"""

        import os
        import shutil

        for src_dir, dirs, files in os.walk(src):
            dst_dir = src_dir.replace(src, dest)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            for file_ in files:
                src_file = os.path.join(src_dir, file_)
                dst_file = os.path.join(dst_dir, file_)
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                shutil.copy(src_file, dst_dir)

    def convert(self, project_title=None):
        import os
        import shutil
        print("Creating project directory")
        project_dir = project_title or self.APP_NAME.replace("app", "project")
        try:
            os.makedirs(project_dir)
        except OSError, e:
            print("{} already exsists".format(project_dir))
        os.chdir(project_dir)
        print ("Creating app directory ({})".format(self.APP_NAME))
        try:
            os.makedirs(self.APP_NAME)
            with open(os.path.join(self.APP_NAME, "__init__.py"), 'w'):
                pass
        except OSError, e:
            print("Directory {} already exists".format(self.APP_NAME))

        print ("Creating __init__.py")
        with open("__init__.py", 'w'):
            pass

        print("Creating models.py")
        with open(os.path.join(self.APP_NAME, "models.py"), 'w') as models:
            models.write(self._create_models())

        print("Creating test.py")
        with open(os.path.join(self.APP_NAME, "tests.py"), 'w'):
            pass

        print("Creating views.py")
        with open(os.path.join(self.APP_NAME, "views.py"), 'w') as views:
            views.write(self._create_views())

        if self.smart_return:
            print("Creating middleware.py")
            with open(os.path.join(self.APP_NAME, "middleware.py"), 'w') as middleware:
                middleware.write(self._create_middleware())

        if os.path.exists("../templates") and os.path.isdir("../templates/"):
            print("Copying templates")
            dest = os.path.join(self.APP_NAME, "templates", self.APP_NAME)
            self._copy_and_replace("../templates/", os.path.join(
                                    self.APP_NAME, "templates"))

        if os.path.exists("../static") and os.path.isdir("../static/"):
            print("Copying static")
            self._copy_and_replace("../static/", os.path.join(self.APP_NAME,
                                                    "static"))

        if os.path.exists("../db.sqlite"):
            print("Copying db.sqlite")
            shutil.copy("../db.sqlite", "db.sqlite")

        print("Creating setings.py")
        with open("settings.py", 'w') as settings:
            settings.write(self._create_settings())

        print("Creating urls.py")
        with open("urls.py", 'w') as urls:
            urls.write(self._create_urls())

        print("Creating manage.py")
        with open("manage.py", 'w') as manage:
            manage.write(self._create_manage())
            os.chmod("manage.py", 0755)

        os.chdir("..")



import sys
d = D()
sys.modules["importd.d"] = d
