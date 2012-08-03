class D(object):
    from django.conf.urls.defaults import patterns, url
    urlpatterns = patterns("")
    class BadCall(Exception): pass
    
    def is_management_command(self, cmd):
        return cmd in "runserver,shell".split(",")
    
    def handle_management_command(self, cmd, *args, **kw):
        from django.core import management
        management.call_command(cmd, *args, **kw)
        
    def update_regexers(self, regexers):
        pass
    
    def update_urls(self, urls):
        self.urlpatterns += urls
        
    def import_django(self):
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
    
    def add_view(self, regex, view, *args, **kw):
        self.urlpatterns += self.patterns("", self.url(regex, view, *args, **kw))
    
    def decorate_return(self, view):
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
            
    def translate_regex(self, regex): return regex
    
    def __call__(self, *args, **kw):
        print "__call__", args, kw
        if args:
            if self.is_management_command(args[0]):
                self.handle_management_command(*args, **kw)
                return self 
            if type(args[0]) == list:
                self.update_urls(args[0])
                return self
            if callable(args[0]):
                decorated = self.decorate_return(args[0])
                self.add_view("^%s/$" % args[0].__name__, decorated)
                return decorated
            def ddecorator(view):
                decorated = self.decorate_return(view)
                self.add_view(
                    self.translate_regex(args[0]), decorated, *args[1:], **kw
                )
                return decorated
            return ddecorator
        else:
            if "regexers" in kw: 
                self.update_regexers(kw.pop("regexers"))
            if "no_atexit" in kw:
                self.no_atexit = kw.pop("no_atexit")
            from django.conf import settings
            kw["ROOT_URLCONF"] = "amitu.d"
            if "TEMPLATE_DIRS" not in kw:
                kw["TEMPLATE_DIRS"] = ("templates",)
            settings.configure(**kw)
            self.settings = settings
            self.import_django()
        return self

    def atexit(self):
        """
        >>> from django.core import management
        >>> help(management)

        >>> management.execute_from_command_line
        <function execute_from_command_line at 0x106a4d5f0>
        >>> management.execute_from_command_line()
        """
        if hasattr(self, "no_atexit") and self.no_atexit: return
        self.handle_management_command("runserver", "8000")
        
import sys, atexit
d = D()
atexit.register(d.atexit)
sys.modules["amitu.d"] = d
