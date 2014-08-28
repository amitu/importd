from importd import d
from django.conf import settings

settings.VIEWS_IMPORTED=True

@d
def test1(request):
    return "test1.html", {"the_answer": 42}

@d
def test2(request):
    ctx = {
        'sample_list': range(3),
    }
    return d.render_to_response("test2.jinja", ctx)
