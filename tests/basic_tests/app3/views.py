from importd import d, Blueprint

bp = Blueprint()

@bp
def index3(request):
    return d.HttpResponse("app3/index")

@bp('/demo/url', name='demo-url')
def demo_url(request):
    return d.HttpResponse("app3/demo-url")
