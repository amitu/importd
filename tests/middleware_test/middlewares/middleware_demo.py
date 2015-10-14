from django.http import HttpResponse

class middleware_demo(object):
    def process_view(self, request, view, *args, **kwargs):
        return HttpResponse("middleware_called")
