Django Generic Form Handler View -- fhurl
*****************************************

importd is the fastest way to django. No project creation, no apps, no
settings.py, just an import.

Installation::

    $ easy_install importd

importd is being developed on http://github.com/amitu/importd/.

See the Changelog: https://github.com/amitu/importd/blob/master/ChangeLog.rst.

hello world with importd
------------------------

With importd there is no need to create a django project or app. There is no
settings.py or urls.py, nor is there a need of manage.py. A single file is
suffecient, eg hello.py::

    from importd import d

    @d("/")
    def index(request):
        return d.HttpResponse("hello world")

To run this hello.py:

.. code-block:: sh
    $ python hello.py
    Validating models...

    0 errors found
    Django version 1.4.1, using settings None
    Development server is running at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.

To see if it works:

.. code-block::sh
    $ curl "http://localhost:8000"
    hello world

atexit magic
------------

importd uses atexit to magically call runserver as seen in previous case. This
can be disabled by calling d(no_atexit=True).

management commands
-------------------

importd, along with atexit magic acts as management command too:

.. code-block::sh

    $ python hello.py help shell
    python hello.py help shell (02-18 21:14)
    Usage: hello.py shell [options] 

    Runs a Python interactive interpreter. Tries to use IPython or bpython, if one of them is available.

    Options:
      -v VERBOSITY, --verbosity=VERBOSITY
                            Verbosity level; 0=minimal output, 1=normal output,
                            2=verbose output, 3=very verbose output
      --settings=SETTINGS   The Python path to a settings module, e.g.
                            "myproject.settings.main". If this isn't provided, the
                            DJANGO_SETTINGS_MODULE environment variable will be
                            used.
      --pythonpath=PYTHONPATH
                            A directory to add to the Python path, e.g.
                            "/home/djangoprojects/myproject".
      --traceback           Print traceback on exception
      --plain               Tells Django to use plain Python, not IPython or
                            bpython.
      -i INTERFACE, --interface=INTERFACE
                            Specify an interactive interpreter interface.
                            Available options: "ipython" and "bpython"
      --version             show program's version number and exit
      -h, --help            show this help message and exit


automatically configure django
------------------------------

`importd` sets DEBUG to true.

manually configuring django
---------------------------

`importd` automatically configures django when needed. This can be disabled by 
calling d(dont_configure=True) before any other importd functionality.

gunicorn server
---------------

importd works with gunicorn server, which is recommended for production setup
instead of runserver command seen above, which is good only for debugging.

gunicorn is a dependency of importd, so if you have importd installed properly,
gunicorn should be in your path.

Running hello.py with gunicorn:

.. code-block::sh

    $ gunicorn -w 2 hello:d
    2013-02-18 21:20:06 [50844] [INFO] Starting gunicorn 0.17.2
    2013-02-18 21:20:06 [50844] [INFO] Listening at: http://127.0.0.1:8000 (50844)
    2013-02-18 21:20:06 [50844] [INFO] Using worker: sync
    2013-02-18 21:20:06 [50847] [INFO] Booting worker with pid: 50847
    2013-02-18 21:20:06 [50848] [INFO] Booting worker with pid: 50848

autoconfigution of templates
----------------------------

importd automatically includes templates folder in directory containing hello.py
to TEMPLATE_DIRS settings.

auto configuration of static folder
-----------------------------------

importd automatically maps /static/ path to folder named `static`, in the same
directory as hello.py.

importd is relocatable
----------------------

importd based script, like hello.py can be invoked from any folder, templates
and static folders would be properly configured.

.. code-block::sh
    
    $ cd /any/folder
    $ python /full/path/to/hello.py
    Validating models...

    0 errors found
    February 18, 2013 - 21:23:11
    Django version 1.5c1, using settings None
    Development server is running at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.

If in your program you need to refer to local path, call d.dotslash(path) method
to translate relative paths to absolute paths properly, so your program
continues to be relocatable.

auto configuration of sqlite3 as database
-----------------------------------------

For testing many a times sqlite is suffecient, and for those times importd
automatically configures django with sqlite3 as database, with sqlite file
stored in `db.sqlite` in the same folder as hello.py.

This can be disabled by passing actual database settings DATABASES to d(). 

@d decorator
------------

importd has a decorator that can be applied to any view to add it to URLS. By
default the @d decorator takes the name of the view method, and constructs the
url /method-name/.::

    from importd import d

    @d
    def hello(request):
        return d.HttpResponse("hey there!")

In this case, importd will map hello() method to /hello/ url. This can be
overriden by passing the URL where the view must be mapped to @d::

Since importd uses smarturls underneath this is equivalent to::

    from importd import d

    @d("^$")
    def hello(request):
        return d.HttpResponse("hey there!")

In this case hello method is mapped to /.

@d decorator also supprts named urls via name keyword argument, eg::

    form importd import d

    @d("^home/$", name="home")  # named urls
    def home(request):
        return "home.html"

auto imports
------------

Since most views.py methods will be defined in views.py of respective
application, importd automatically imports views module of all apps configured
to make sure all such decorators get called when django is configured.

For convenience importd also imports forms modules and signals modules of each
app configured.

importd works well with smarturls
---------------------------------

Since importd uses smarturls underneath this::

    from importd import d

    @d("^$")
    def hello(request):
        return d.HttpResponse("hey there!")

is equivalent to::

    from importd import d

    @d("/")
    def hello(request):
        return d.HttpResponse("hey there!")

Notice the simpler URL passed to @d("/") instead of d("^$"). Either form can be
used.

Take a look at smarturls documentation to see how smarturls can simplfy url
construction for you.

importd works well with fhurl
-----------------------------

views can return non HttpResponse objects
-----------------------------------------

Django views are expected to only return HttpResponse based objects. importd
allows you to do more than this. 

A view can return a string, which is treated as name of template, which is
rendered with RequestContext and returned. A view can also return a tuple of
(str, dict), in this case the str is treated as name of view, and dict as the
context::

    from importd import d
    import time

    @d # /index/, url derived from name of view
    def index(request):
        return "index.html", {"msg": time.time()}

Further a view can also return arbitrary data structures not mentioned above, in
such cases importd will convert that to JSON and return it to client::

    from importd import d

    @d  # served at /json/, converts object to json string, with proper mimetype
    def json(request):
        return {
            "sum": (
                int(request.GET.get("x", 0)) + int(request.GET.get("y", 0))
            )
        }

importd comes with convenience JSONResponse class to return arbitrary json
object that may be a string, or a (string, dict) tuple.

disabling auto configuration
-----------------------------

All such configuration should be done at the beginning of the program.

importd with existing apps
--------------------------

Nothing special has to be done to work with existing apps, django specific
INSTALLED_APPS must contain the name of apps as usual, and it can be passed to
d() method::

    from importd import d

    d(INSTALLED_APPS=["django.contrib.auth", "django.contrib.contenttypes"])

    from django.contrib.auth.models import User

    @d("/<int:userid>/")
    def hello(request, userid):
        user = User.objects.get(userid)
        return d.HttpResponse("hey there %" % user)

importd and custom models
-------------------------

To create custom models, create an app using $ python hello.py startapp
hello_app and add it to INSTALLED_APPS.

