# foo.py
from amitu import d

# key advantages:
# 1. single file app
# 2. still fully compatible with existing django projects
# 3. auto matic url regex creation
# 4. all frequently used django functions/classes collected in d.* namespace
# Note: not yet sure if all of this is possible :-p

d(							# callable modules are magic. some magic is good.
	DEBUG = True,
	urls = (
		("^admin/", d.include("django.contrib.auth")), 
	),
	INSTALLED_APPS = ("django.contrib.admin", "foo"),
	TEMPLATES_DIR = [d.dotslash("templates")],
	regexers = {
		"domain": regex_for_domain,
	}
)

from foo.models import Foo 	   # define custom models in models.py as usual

@d("/", name="index") # named url
def index(request):
	return "index.html", {} # {} optional

@d 		# equivalent of @d("/whoami/")
def whoami(request):
	return d.HttpResponse("amitu")

@d("/<username>/", "/user/<username>") # both urls point to same view
def user(request, username):
	if request.path.startswith("/user/"): 
		return d.HttpResponseRedirect("/%s/" % username)
	# lots of django helpers available with d.something
	foo = d.get_object_or_404(Foo, username=username)
	return "user.html", {"foo": foo}

# things in <> can have type too, sytax is <type:name>
@d("/blog/<int4:year>/<word:month>/<int2:day>/<slug:title>/") # auto regexes
def blog_post(request, year, month, day, title):
	pass
	
@d("/domain/<domain:site>") 	# custom types can be defined in setting call
def show_domain(request, site):
	pass
	
@d("/do-something", template="some-form.html") # fhurl integrated
class SomeForm(d.RequestForm):
	somefield = d.forms.CharField()
	def save():
		pass
	
if __name__ == "__main__":
	#d("shell")
	d("runserver", 8000, host="foo") # can also read host:port from sys.argv