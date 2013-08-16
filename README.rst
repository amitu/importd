What is it?
===========

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

.. code::

  $ python foo.py

This will start the debug server.

To run it in production:

.. code::

  $ gunicorn foo:d

Some examples: https://github.com/amitu/importd/tree/master/examples

Backward Incompatibility Change
===============================

d.main() used to be not required, now it is.

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

Installation
============

.. code::

 $ pip install importd

Documentation
=============

docs: http://packages.python.org/importd

ChangeLog
=========

https://github.com/amitu/importd/blob/master/ChangeLog.rst

Contributors
============

  * Amit Upadhyay (https://github.com/amitu)
  * Dmytro Vorona (https://github.com/alendit)
  * Jannis Leidel (https://twitter.com/jezdez)
  * Lukasz Balcerzak (https://github.com/lukaszb)

LICENSE
=======

 * BSD
