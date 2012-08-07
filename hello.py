from importd import d

d(dont_configure=True)

@d("/")
def hello(request):
    return d.HttpResponse("hello world")
