0.1.2 - 13-Aug-2012
===================

 * few bug fixes, APP_DIR was calculated incorrectly
 * automatically configure databases if DATABASES is not passed
 * auto import .views and .forms of each installed app to give all
   @d("pattern") decorators visibility
 * auto import .signals in each app to allow signals to register themselve,
   better than import them from models.py explicitly and fighting the circular
   imports issue

0.1.1 - 8-Aug-2012
==================

 * refactored out smarturls into a separate project

0.1.0 - 6-Aug-2012
==================

Initial release.

