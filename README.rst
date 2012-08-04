docs: http://packages.python.org/amitu-d/ (coming soon)

Features
========

 * minimal app: https://github.com/amitu/amitu-d/blob/master/foo.py
 * run debug server: $ python foo.py
 * management commands still available: $ python foo.py shell
 * gunicorn support: $ gunicorn foo:d
 * easier url construction eg "/edit/<int:id>/" instead of "^edit/(?P<id>\d+)/$"
 
ToDo
====

 * figure our whats going on with double imports
 * figure out whats going on when gunicorn exits
