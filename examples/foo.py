from importd import d

d(
	DEBUG=True,
	SMART_RETURN=True,
)  # configure django

def real_index2(request):
    return d.HttpResponse("real_index2")

d(# configure other urlpatterns
    d.patterns("",
        ("^$", real_index2),
    )
)

@d  # /index/
def index(request):
    import time
    return "index.html", {"msg": time.time(),
						  "objs": d.models.TestModel.objects.all()}

@d("^edit/$", name="edit")  # named urls
def real_index(request):
    return "home.html"

@d  # served at /json/, converts object to json string
def json(request):
    return {"sum": int(request.GET.get("x", 0)) + int(request.GET.get("y", 0))}

@d("^fhurl/$")
class MyForm(d.RequestForm):
    x = d.forms.IntegerField()
    y = d.forms.IntegerField()

    def save(self):
		x, y = self.cleaned_data['x'], self.cleaned_data['y']
		d.models.TestModel.objects.create(x=x, y=y)
		return x + y


class TestModel(d.models.Model):
    x = d.models.CharField(max_length=20)
    y = d.models.CharField(max_length=20)


if __name__ == "__main__":
    d.main()
