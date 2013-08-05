from importd import d
from django.conf import settings

settings.VIEWS_IMPORTED=True

@d
def test1(request):
    return "test1.html", {"the_answer": 42}
