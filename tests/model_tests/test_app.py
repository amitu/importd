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


class TestModel(d.models.Model):
    value = d.models.CharField(max_length=20)

if __name__ == "__main__":
    d.main()