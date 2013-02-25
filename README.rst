What is it?
===========

Django is awesome, but starting a new project in it is a pain. importd is
inspired from ruby's sinatra. Hello world django project:

.. code-block:: python

    from importd import d
    d(DEBUG=True)

    @d("/")
    def idx(request):
        return "index.html", {"ids":
        					 d.models.Index.objects.all()}

    @d("/post/<int:post_id>/")
    def post(request, post_id):
    	d.models.Index.objects.create(post_id=post_id)
        return "post.html", {"post_id": post_id}
        
    class Index(d.models.Model):
    	post_id = d.models.CharField(max_length=10)

    if __name__ == "__main__":
        d.main()


To run it:

.. code::

  $ python foo.py

This will start the debug server. 

To run it in production:

.. code::

  $ gunicorn foo:d

To convert to standard django project:

.. code::

  $ python foo.py convert

or:

.. code::

  $ python foo.py convert project_name

Some examples: https://github.com/amitu/importd/tree/development/examples

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
 * easy convertable to django project structure

Installation
============

.. code::

 $ easy_install importd

Documentation
=============

docs: http://amitu.com/importd/

ToDo/Known Issues
=================

 * figure our whats going on with double imports
