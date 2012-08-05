from importd import d

d(DEBUG=True) # configure django

def real_index2(request):
    return d.HttpResponse("real_index2")
    
d(      # configure other urlpatterns
    d.patterns("",
        ("^$", real_index2),
    )
)

@d # /index/
def index(request):
    import time
    return "index.html", {"msg": time.time()}

@d("^home/$", name="home")  # named urls
def real_index(request):
    return "home.html"
    
@d  # served at /json/, converts object to json string
def json(request):
    return {"sum": int(request.GET.get("x", 0)) + int(request.GET.get("y", 0))}

@d("/edit/<int:id>/", name="edit_page")
def edit(request, id):
    return {"id": id}
    
@d("^fhurl/$")
class MyForm(d.RequestForm):
    x = d.forms.IntegerField()
    y = d.forms.IntegerField()
    
    def save(self):
        return self.cleaned_data["x"] + self.cleaned_data["y"]
