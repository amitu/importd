from importd import d

@d("/")
def hello(request):
    return d.HttpResponse("hello world")
