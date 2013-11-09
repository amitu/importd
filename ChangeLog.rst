importd ChangeLog
=================

0.2.9 - 10-Nov-2013
-------------------

 * there was a bug in previous release, d.dotslash() always returned the same
   value if called before configuring django

0.2.8 - 10-Nov-2013
-------------------

 * integrated with speaklater(optional), if available, d.dotslash() can be used
   before django is configured, returns a lazy string, which becomes
   "available" after django has been configured. suitable for configuring
   template dirs or static files etc.

0.2.7 - 4-Nov-2013
------------------

 * db kwarg can not be a string or (string, dict), in later case dict would be
   merged into dict returned by dj_database_url.parse(), to support extra
   settings django allows eg OPTIONS, CONN_MAX_AGE[this one I particularly need
   in every projct, and dont want to miss out on using dj_database_url]

0.2.6 - 4-Nov-2013
------------------

 * support for django 1.6c1

0.2.5 - 4-Nov-2013
------------------

 * now accepts db= kward when configuring, uses dj_database_url to parse db

0.2.4 - 4-Nov-2013
------------------

 * changes to serve admin static files

0.2.3 - 16-Aug-2013
-------------------

 * turns out importd depends on django :-)

0.2.2 - 12-Aug-2013
-------------------

 * support for django 1.3.7
 * testing django 1.5.2, 1.4.6 now.

0.2.1 - 12-Aug-2013
-------------------

 * packaging was broken, thank you @jezdez

0.2.0 - 4-Aug-2013
------------------

There is a backward incompatible change in this release. importd has removed
atexit magic, which means a call to d.main() must be included somewhere.

.. code-block:: python

    from importd import d

    @d("/")
    def hello(request):
        return d.HttpResponse("hello world")

    if __name__ == "__main__":
        d.main() # NOTE THIS

 * BACKWARD INCOMPATIBLE: remove atexit magic, d.main() is the replacement
 * gunicorn cleanly exits now
 * tests, support django 1.4.3 and 1.5.1 for each of python 2.6, 2.7 and 3.3
 * less magic, no more sys.modules tweaking
 * runserver now reloads when any file changes
 * added auto generated MANIFEST.in (using check-manifest)
 * added support for mounting urls to custom locations

0.1.4 - 22-Oct-2012
-------------------

 * setup.py was buggy

0.1.3 - 22-Oct-2012
-------------------

 * setup.py was buggy

0.1.2 - 13-Aug-2012
-------------------

 * few bug fixes, APP_DIR was calculated incorrectly
 * automatically configure databases if DATABASES is not passed
 * auto import .views and .forms of each installed app to give all
   @d("pattern") decorators visibility
 * auto import .signals in each app to allow signals to register themselve,
   better than import them from models.py explicitly and fighting the circular
   imports issue

0.1.1 - 8-Aug-2012
------------------

 * refactored out smarturls into a separate project

0.1.0 - 6-Aug-2012
------------------

Initial release.

