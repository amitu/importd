from importd import d


@d
def index2(request):
    return d.HttpResponse("app2/index")
