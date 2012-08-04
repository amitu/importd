What is it?
===========

Django is awesome, but starting a new project in it is a pain. amitu.d is inspired from ruby's sinatra. Hello world django project:

.. code::

 from amitu import d
 d(DEBUG=True)

 @d("/")
 def idx(request):
    return "index.html" 

 @d("/post/<int:post_id">/")
 def post(request, post_id):
    return "post.html", {"post_id": post_id}

To run it:

.. code::

  $ python foo.py

This will start the debug server. 

To run it in production:

.. code::

  $ gunicorn foo:d	

Features
========

 * minimal app: https://github.com/amitu/amitu.d/blob/master/foo.py
 * run debug server: $ python foo.py
 * automatically maps "templates" folder in foo.py directory to serve templates
 * automatically maps "static" folder in foo.py to serve static content
 * management commands still available: $ python foo.py shell
 * gunicorn support: $ gunicorn foo:d
 * works seamlessly with fhurl (http://packages.python.org/fhurl/)
 * easier url construction eg "/edit/<int:id>/" instead of "^edit/(?P<id>\d+)/$"
 
Installation
============

.. code::

 $ easy_install amitu.d

Documentation
=============

docs: http://packages.python.org/amitu.d/ (coming soon) 

ToDo/Known Issues
=================

 * figure our whats going on with double imports
 * figure out whats going on when gunicorn exits
