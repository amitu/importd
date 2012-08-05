class D(object):
    from django.conf.urls.defaults import patterns, url
    import re
    urlpatterns = patterns("")
    regexers = {
        "word": "\w+",
        "digit": "\d",
        "int": "\d+",
        "int2": "\d{2,2}",
        "int4": "\d{4,4}",
    }
    _R = re.compile("<((\w+:)?\w+)>")
    def _is_management_command(self, cmd):
        return cmd in "runserver,shell".split(",")
    
    def _handle_management_command(self, cmd, *args, **kw):
        from django.core import management
        management.call_command(cmd, *args, **kw)
        
    def update_regexers(self, regexers):
        self.regexers.update(regexers)
    
    def update_urls(self, urls):
        self.urlpatterns += urls
        
    def _import_django(self):
        from django.http import HttpResponse, Http404, HttpResponseRedirect
        self.HttpResponse = HttpResponse
        self.Http404 = Http404
        self.HttpResponseRedirect = HttpResponseRedirect
        from django.shortcuts import get_object_or_404, render_to_response
        self.get_object_or_404 = get_object_or_404
        self.render_to_response = render_to_response
        from django.conf.urls.defaults import patterns, url
        self.patterns = patterns
        self.url = url
        from django.template import RequestContext
        self.RequestContext = RequestContext
        from django.core.wsgi import get_wsgi_application
        self.wsgi_application = get_wsgi_application()
        from django import forms
        self.forms = forms
        from fhurl import RequestForm, fhurl
        self.fhurl = fhurl
        self.RequestForm = RequestForm

    def dotslash(self, pth):
        import os
        return os.path.join(self.APP_DIR, pth)
        
    def add_view(self, regex, view, *args, **kw):
        self.urlpatterns += self.patterns("", self.url(regex, view, *args, **kw))
        
    def add_form(self, regex, form_cls, *args, **kw):
        self.urlpatterns.append(self.fhurl(regex, form_cls, *args, **kw))
    
    def _decorate_return(self, view):
        import functools
        @functools.wraps(view)
        def decorated(request, *args, **kw):
            res = view(request, *args, **kw)
            if isinstance(res, basestring):
                res = res, {}
            if isinstance(res, tuple):
                template_name, context = res
                res = self.render_to_response(
                    template_name, context, self.RequestContext(request)
                )
            else:
                import fhurl
                res = fhurl.JSONResponse(res)
            return res   
        return decorated
    
    def _regex_substituter(self, m):
        name = m.groups()[0]
        if ":" not in name: name = "word:%s" % name
        t, n = name.split(":")
        return "(?P<%s>%s)" % (n, self.regexers[t])
        
    def translate_regex(self, regex):
        if not regex.startswith("/"): return regex
        return "^%s$" % self._R.sub(self._regex_substituter, regex)[1:]
    
    def __call__(self, *args, **kw):
        #print "__call__", args, kw
        if args:
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
                if type(candidate) == forms.DeclarativeFieldsMetaclass:
                    self.add_form(
                        self.translate_regex(args[0]), candidate, *args[1:], **kw
                    )
                    return candidate
                decorated = self._decorate_return(candidate)
                self.add_view(
                    self.translate_regex(args[0]), decorated, *args[1:], **kw
                )
                return decorated
            return ddecorator
        else:
            import inspect, os
            self.APP_DIR = os.path.dirname(
                os.path.realpath(inspect.stack()[1][1])
            )
            if "regexers" in kw: 
                self.update_regexers(kw.pop("regexers"))
            if "no_atexit" in kw:
                self.no_atexit = kw.pop("no_atexit")
            from django.conf import settings
            kw["ROOT_URLCONF"] = "importd.d"
            if "TEMPLATE_DIRS" not in kw:
                kw["TEMPLATE_DIRS"] = (self.dotslash("templates"),)
            if "STATIC_URL" not in kw:
                kw["STATIC_URL"] = "static/"
            if "STATICFILES_DIRS" not in kw:
                kw["STATICFILES_DIRS"] = (self.dotslash("static"),)
            settings.configure(**kw)
            from django.contrib.staticfiles.urls import staticfiles_urlpatterns
            self.urlpatterns += staticfiles_urlpatterns()
            self.settings = settings
            self._import_django()
        return self

    def _act_as_manage(self):
        from django.core import management
        import sys
        management.execute_from_command_line(sys.argv)
        
    def atexit(self):
        if hasattr(self, "no_atexit") and self.no_atexit: return
        
        import sys
        
        if len(sys.argv) == 1:
            return self._handle_management_command("runserver", "8000")
            
        if len(sys.argv) != 2:
            return self._act_as_manage()
            
        port = sys.argv[1]
        
        try:
            int(port)
        except ValueError:
            if ":" not in port:
                return self._act_as_manage()
            if port.endswith(":d"): return
        
        self._handle_management_command("runserver", port)
        
import sys, atexit
d = D()
atexit.register(d.atexit)
sys.modules["importd.d"] = d
