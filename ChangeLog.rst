importd ChangeLog
=================

0.5.0 - 1-Feb-2016
-------------------
* Django 1.9 Support.  
* Clean Up and Deprecate stuff from https://github.com/amitu/importd/issues/72. 
* Tox Tests from Python2.7 Django1.5 to Python3.5 Django1.9.

0.4.3 - 12-Oct-2015
-------------------
* New tag s added.  
* It is recommended to call d.openenv before calling it in main. 
* Extra python path cannot be added into d as kwargs. 
 
0.4.2 - 9-Oct-2015
------------------
* Fixed process_view of middleware not called. 
* Extra python path can be added into d as kwargs argument ENVDIR. 

0.4.1 - 30-Sep-2015
-------------------
* Fixed AttributeError when calling d.dotslash. 
* don't auto configure ROOT_URLCONF if already configured

0.4.0 - 27-Aug-2015
-------------------

Settings Framework Release

* added `debug` keyword argument that takes dict and is added to base settings
  only if DEBUG is true
* added importd.env, which checks a key in environment and if not present
  returns a default value (so that I do not have to write this utility
  everywhere)
* added a importd.debug() that can be used for conditional settings
* MIDDLEWARE_CLASSES, INSTALLED_APPS or TEMPLATE_CONTEXT_PROCESSORS is looked
  for settings that starts with "debug:", such values are dropped completely in
  prod, and in debug the "debug:" prefix is stripped. similarly we have "prod:".
* created impoortd.e() which can be used to "expose" some of the settings to
  template. in order to use it in template, add a template context processor
  "importd.esettings", this will make available a variable named "esettings".


0.3.3 - 24-Feb-2015
-------------------

* added livereload command/feature.


0.3.2 - 27-Jan-2015
-------------------

* Added blueprint document.
* calling django.setup() when available


0.3.1 - 27-Oct-2014
-------------------

* released without blueprint thing. rereleasing.


0.3.0 - 27-Oct-2014
-------------------

* Changed default setting STATIC_ROOT from ``static`` to ``staticfiles`` and set new default setting STATICFILES_DIRS to ``static``. This means that if you use the collectstatic management command, it will collect the files from the ``static`` folder and copy them to ``staticfiles``. If you use an external web server, you have to change the local path of the url http://server/static/ to serve files from the ``staticfiles`` folder.
* Auto Add django-debug-toolbar: try to import it, if sucessful and is not on settings and the database exist(debug_toolbar needs a DB) and DEBUG=True, then configure debug_toolbar.
* Auto Add SECRET_KEY: If no SECRET_KEY on settings, try to read SECRET_KEY from ./secret.txt , if no ./secret.txt generate a random string then write it to ./secret.txt and finally return it as SECRET_KEY.
* Auto Add django.contrib.humanize.
* Auto Add django.contrib.staticfiles.
* Auto Import get_list_or_404, render, redirect from django.shortcuts.
* Fixed Tests for new features.
* Support django-debug-toolbar 1.2.1
* Add importd-boilerplate hyperlink.
* Auto Add coffin/django-jinja.
* Added support for Django1.7 and Python3.4, removed support for python3.3.
* Added autoimport keyword argument, to control if views etc should be auto
  imported.
* Added a blueprint like framework inspired from flask


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

* db kwarg can now be a string or (string, dict), in later case dict would be
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
