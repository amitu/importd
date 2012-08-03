import time
print time.time()
from amitu import d
print time.time()
d(DEBUG=True)
print time.time()

print d.settings.DEBUG
print d.settings.TEMPLATE_DIRS
print time.time()

from amitu.d import settings
print settings.DEBUG
print time.time()

#d("shell")
print d.BadCall
print time.time()
try:
    d("foo")
except d.BadCall:
    print "ex"
print time.time()

print d.HttpResponse

@d
def index(request):
    return d.HttpResponse("index!")
    
#d("runserver", "0.0.0.0:8080")