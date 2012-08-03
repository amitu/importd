#!/usr/bin/env python
from amitu import d
import time

d(DEBUG=True, no_atexit=True)

def real_index2(request):
    return d.HttpResponse("real_index2")
    
d(
    d.patterns("",
        ("^$", real_index2),
    )
)

@d # /index/
def index(request):
    return "index.html", {"msg": time.time()}

#@d("^$") # /
@d
def real_index(request):
    return "home.html"
    
@d
def json(request):
    return {"sum": int(request.GET.get("x", 0)) + int(request.GET.get("y", 0))}
