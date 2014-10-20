from importd import d


@d("/view/")
def view(request):
    return d.HttpResponse("yo")
