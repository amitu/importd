# make sure to use importd from the repository
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from importd import d

d(INSTALLED_APPS=["app"])

@d("/")
def main(request):
    objects = TestModel.objects.all()
    return d.HttpResponse("\n".join(map(lambda obj: obj.value, objects)))


@d("add/(?P<value>.*)")
def add(request, value):
    TestModel.objects.create(value=value)
    return d.HttpResponse("Success!")

#@register_admin?
class TestModel(d.models.Model):
    value = d.models.CharField(max_length=20)

d.register_admin(TestModel)

if __name__ == "__main__":
    d.main()
