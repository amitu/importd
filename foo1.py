from amitu import d

d(DEBUG=True)

print d.settings.DEBUG
print d.settings.TEMPLATE_DIRS

from amitu.d import settings
print settings.DEBUG

d("shell")
print d.BadCall
try:
    d("foo")
except d.BadCall:
    print "ex"
d("runserver", 8080, host="0.0.0.0")