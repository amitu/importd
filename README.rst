Issues you can help with right now: |waffle|

Build Status: |build-status|

.. |waffle| image:: https://badge.waffle.io/amitu/importd.png?label=ready&title=Ready 
 :target: https://waffle.io/amitu/importd
 :alt: 'Stories in Ready'

.. |build-status| image:: https://travis-ci.org/amitu/importd.png?branch=master
    :target: https://travis-ci.org/amitu/importd


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
=============================

* Simple example : https://github.com/amitu/importd/tree/master/examples
* importd-boilerplate : https://github.com/if1live/importd-boilerplate

  * importd + jinja2 + django-debug-toolbar + django REST framework


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
* Auto SECRET_KEY: If no SECRET_KEY on settings, try to read SECRET_KEY from ./secret.txt , if no ./secret.txt generate a random string then write it to ./secret.txt and finally return it as SECRET_KEY.
* Auto Add coffin/django-jinja (jinja2 integration)

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

Contribution Guide
==================

To view this file, or any restructuredtext file locally before comitting on
git, install restview from pypi.

**Pull Requests**: If you fork this repository to send pull request, please
create a branch for your work instead of working directly on master. This way
your master will track my master, and in case the pull request is rejected, or
delayed, your master stays clean. This also makes easy to send more than one
pull requests from your fork.

LICENSE
=======

* BSD
