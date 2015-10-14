Issues you can help with right now: |waffle|

Build Status: |build-status| |build-health|

.. |waffle| image:: https://badge.waffle.io/amitu/importd.png?label=ready&title=Ready
    :target: https://waffle.io/amitu/importd
    :alt: 'Stories in Ready'

.. |build-status| image:: https://travis-ci.org/amitu/importd.png?branch=master
    :target: https://travis-ci.org/amitu/importd

.. |build-health| image:: https://landscape.io/github/amitu/importd/master/landscape.svg
   :target: https://landscape.io/github/amitu/importd/master
   :alt: Code Health

What is importd?
================

Slides of a talk I gave about importd: http://amitu.com/importd/

Django is awesome, but starting a new project in it is a pain. importd is
inspired from ruby's sinatra. Hello world django project:

.. code-block:: python

    from importd import d
    d(DEBUG=True)

    @d("/")
    def idx(request):
        return "index.html"

    @d("/post/<int:post_id>/")
    def post(request, post_id):
        return "post.html", {"post_id": post_id}

    if __name__ == "__main__":
        d.main()

To run it:

.. code:: bash

  $ python foo.py

This will start the debug server.

To run it in production:

.. code:: bash

  $ gunicorn foo:d

Examples
========

* Simple example : https://github.com/amitu/importd/tree/master/examples
* importd-boilerplate : https://github.com/if1live/importd-boilerplate

  * importd + jinja2 + django-debug-toolbar + django REST framework

Settings Framework
==================

Managing settings in django is done via a settings.py file. Then people put a
``local_settings.py`` to override. This does not scale too well, we end up
having very big settings file with almost no structure, and there are many
issues because of lack of synchronization of ``local_settings.py`` among
developer's machines.

importd has some methods to hopefully make this simpler and more standardized.

First of all there is no ``local_settings.py``. Setting customization are of two
kinds, picking different things for development and prod, eg you want to
activate statsd for prod, but debug_toolbar for development. Both these should
be checked in so there is no scope of people not getting some setting
accidentally. Then there are setting customization for not storing some things
in version control system, say passwords and access tokens and keys. These
should be managed via environment variable.

And then there is also a concern of exposing settings to template. We have a
template context processor, which can expost whole settings to templates, but
that is uncomfortable to many. You may want to expose only a small subset of
things you describe in settings, and you want to do this with minimal fuss.

``importd.env``
---------------

With that in mind importd has ``env()``, which simply reads data from
enironment. So in your app.py you can do:

.. code:: python

    from importd import d, env
    d(
        DEBUG=not env("IS_PROD", False),
        db=env("DB_URL", "mysql://root:@localhost/dbname")
    )

It is highly recommended you include ``envdir`` in your project. May be someday
importd will auto detect envdir and set it up.

``env`` is pretty smart, it takes ``default=`` and ``factory=``. If ``default``
is passed, the string value of environment variable is converted to the
``type()`` of ``default``. You can overwrite this behaviour by passing your own
``factory``, or you can disable this behaviour altogether by passing
``factory=importd.NotSet``.

``env()`` also treats booleans by converting strings like "False/off/no" (case
insensitive) to python's ``False`` value (and non empty string to True as
``bool()`` does).

``importd.debug``
-----------------

With ``.debug()`` you can set some setting to have different values based on
``DEBUG``.

.. code:: python

    from importd import d, debug
    d(
        DEBUG=not env("IS_PROD", False),
        STATSD_CLIENT=debug(
            'django_statsd.clients.toolbar', prod='django_statsd.clients.normal'
        ),
    )

This will set ``STATSD_CLIENT`` to appropriate value based on if we are in debug
mode or not. This is as simple as putting an if condition, but it gets repeated
so many times, its worth using this shortcut. Also this way things stay in same
place, you do not look for up and down the settings file, and in
local_settings.py to see if the variable has been overwritten.

``importd.e``
-------------

This lets you "expose" a setting for access in templates. You should not use
``"django.core.context_processors.settings"`` as a
``TEMPLATE_CONTEXT_PROCESSORS``, instead use ``"importd.esettings"`` context
preprocessor, and in templates you will have access to ``esettings`` variable.

To mark a variable as exposed you have to do this:

.. code:: python

    from importd import d, e

    d(
        DEBUG=True,
        SOME_VAR=e("its value"),
    )

This will make ``SOME_VAR`` available in settings as well as in ``esettings``.

``importd.s``` parameter
-------------------------
This lets you re-use settings variables. In settings file we define variables 
and reuse them when needed. In importd you can reuse defined settings variables.

.. code:: python
    from importd import d, s
     
    d(
        DEBUG=True, 
        TEMPLATE_DEBUG=s("DEBUG")
    ) 

This will set ``TEMPLATE_DEBUG`` settings variable to ``DEBUG`` value. 
``s`` will raise ``ImproperlyConfiguredError`` exception if you will try to use 
it inside of key value. 

.. code:: python
    from importd import d, s

    d(
        EMAIL="foo@example.com",
        ADMINS=(s("EMAIL"), "hello@example.com")
    )

Above example will raise ``ImproperlyConfiguredError``. 

``d(debug={})`` parameter
-------------------------

Some settings are only needed in debug environment, or need to be overwritten,
you can use the ``debug=`` keyword argument to set things up.

.. code:: python

    from importd import d

    d(
        DEBUG=False,
        SOME_VAR="this is prod value",
        debug=dict(
            SOME_VAR="this is debug value"
        )
    )

You can also use `importd.NotSet` as a value in debug dict, and the setting will
be removed altogether in the approprite environment (debug or prod).

d.openenv(path=None)
---------------
Above method will open envdir directory in current directory and will load all 
environment variable inside this directory. If path is realpath i.e. full path
then importd will try to look into specified path. If relative path
specified into path then importd will look relative to current directory. 

It is recommended to call it just after importing d.

debug:/prod: prefix for ``INSTALLED_APPS`` etc
-----------------------------------------------

It is a common pattern that some apps are only needed in debug environment, say
devserver, or debug_toolbar. And since order of apps in ``INSTALLED_APPS``, and
middelware etc is important, we end up copying the whole ``INSTALLED_APPS``,
``MIDDLEWARE_CLASSES`` etc for prod and dev, and this then tend to diverge since
they are in different locations. Not good.

.. code:: python

    from importd import d, env
    d(
        DEBUG=env("IS_PROD", True),
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django.contrib.sessions",

            "debug:devserver",
            "debug:debug_toolbar",

            "myapp"
        ]
    )

Notice the ``debug:`` prefix in ``devserver`` and ``debug_toolbar``. Depending
on the value of ``DEBUG``, these lines would be included or not. importd looks
for strings in ``MIDDLEWARE_CLASSES``, ``INSTALLED_APPS`` and
``TEMPLATE_CONTEXT_PROCESSORS``.

Similarly if something starts with ``prod:``, it is only included in production
environment.

Backward Incompatibile Change
=============================

``d.main()`` used to be not required, now it is.

Features
========

* fully compatible with django
* supports smarturls
* most of regularly used django functions and classes available in d.
  namespace, eg d.HttpResponse, d.render_to_response, d.get_object_or_404 etc
* automatically maps "templates" folder in foo.py directory to serve templates
* automatically maps "static" folder in foo.py to serve static content
* management commands still available: $ python foo.py shell
* wsgi compliant
* gunicorn support
* works seamlessly with fhurl (http://packages.python.org/fhurl/)
* Auto Add django-debug-toolbar (Needs to add it manually to INSTALLED_APPS)
* Auto SECRET_KEY: If no SECRET_KEY on settings, try to read SECRET_KEY from
  ./secret.txt , if no ./secret.txt generate a random string then write it to
  ./secret.txt and finally return it as SECRET_KEY.
* Auto Add coffin/django-jinja (jinja2 integration)
* Support for livereload

Installation
============

.. code:: bash

    $ pip install importd

Documentation
=============

http://importd.readthedocs.org/en/latest/

ChangeLog
=========

https://github.com/amitu/importd/blob/master/ChangeLog.rst

Contributors
============

* Amit Upadhyay (https://github.com/amitu)
* Dmytro Vorona (https://github.com/alendit)
* Jannis Leidel (https://twitter.com/jezdez)
* Lukasz Balcerzak (https://github.com/lukaszb)
* Juan Carlos (https://github.com/juancarlospaco)
* Josep Cugat (https://github.com/jcugat)
* Yu Byunghoo (https://github.com/if1live)
* Arpit Singh (https://github.com/arpitremarkable)
* Hitul Mistry (https://github.com/hitul007)

Contribution Guide
==================

To view this file, or any restructuredtext file locally before comitting on git,
install ``restview`` from pypi.

**Pull Requests**: If you fork this repository to send pull request, please
create a branch for your work instead of working directly on master. This way
your master will track my master, and in case the pull request is rejected, or
delayed, your master stays clean. This also makes easy to send more than one
pull requests from your fork.

LICENSE
=======

* BSD
