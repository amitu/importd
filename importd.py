class D(object):
    from django.conf.urls.defaults import patterns
    urlpatterns = patterns("")

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
        )

    def _iterate_imports(self, callback):
        """Iterates through imports and calls callback for each
        (module_name, attributes) pair. If attribute is a string, it is 
        converted to a list first"""

        for module_name, attributes in self.DJANGO_IMPORT:
            if isinstance(attributes, basestring):
                attributes = [attributes]
            callback(module_name, attributes) 

    def _import_django(self):
        def set_attr(module_name, attributes):
            import importlib
            module = importlib.import_module(module_name)
            for attribute in attributes:
                setattr(self, attribute, getattr(module, attribute))
        self._iterate_imports(set_attr)

        self.wsgi_application = self.get_wsgi_application()



    def dotslash(self, pth):
        import os
        return os.path.join(self.APP_DIR, pth)

    def add_view(self, regex, view, *args, **kw):
        self.urlpatterns += self.patterns(
            "", self.surl(regex, view, *args, **kw)
        )

    def add_form(self, regex, form_cls, *args, **kw):
        self.urlpatterns.append(self.fhurl(regex, form_cls, *args, **kw))

    def _decorate_return(self, view):
        import functools
        @functools.wraps(view)
        def decorated(request, *args, **kw):
            res = view(request, *args, **kw)
            if isinstance(res, basestring):
                res = res, {}
            if isinstance(res, self.HttpResponse): return res
            if isinstance(res, tuple):
                template_name, context = res
                res = self.render_to_response(
                    template_name, context, self.RequestContext(request)
                )
            else:
                res = self.JSONResponse(res)
            return res
        decorated.orig_view = view
        return decorated

    def _configure_django(self, **kw):
        import inspect, os
        self.APP_DIR = os.path.dirname(
            os.path.realpath(inspect.stack()[2][1])
        )

        if "regexers" in kw: 
            self.update_regexers(kw.pop("regexers"))

        from django.conf import settings

        self.settings = settings

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
            if "DEBUG" not in kw: kw["DEBUG"] = True
            settings.configure(**kw)
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
        self._import_django()
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
                decorated = self._decorate_return(args[0])
                self.add_view("^%s/$" % args[0].__name__, decorated)
                return decorated
            def ddecorator(candidate):
                from django.forms import forms
                if type(candidate) == forms.DeclarativeFieldsMetaclass: # unsafe
                    self.add_form(args[0], candidate, *args[1:], **kw)
                    return candidate
                decorated = self._decorate_return(candidate)
                self.add_view(args[0], decorated, *args[1:], **kw)
                return decorated
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
            print(self.create_views())
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
        source_lines = inspect.getsourcelines(view.orig_view)[0]
        # from IPython import embed; embed()
        
        return "\n".join(source_lines[1:])

    def create_views(self):
        import re
        views = []

        for urlpattern in self.urlpatterns:
            # check if its a decorated view from importd
            if hasattr(urlpattern.callback, "orig_view"):
                views.append(self._get_view_source(urlpattern.callback))

        used_imports = set()
        for view in views:
            used_imports.update(re.findall(r'd\.([a-zA-Z]+)', view))


        imports = []
        def create_import_strings(module_name, attributes):
            to_import = used_imports.intersection(attributes)
            if to_import:
                imports.append("from {} import {}".format(
                                                    module_name,
                                                    ", ".join(to_import)))
        self._iterate_imports(create_import_strings)
        return "{}\n\n{}".format("\n".join(imports), "\n\n".join(views))

import sys
d = D()
sys.modules["importd.d"] = d
