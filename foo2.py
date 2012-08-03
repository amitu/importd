#!/usr/bin/env python
from amitu import d
import time

d(DEBUG=True)

@d # /index/
def index(request):
    return "index.html", {"msg": time.time()}

@d("^$") # /
def real_index(request):
    return "home.html"
    
@d
def json(request):
    return {"sum": int(request.GET.get("x", 0)) + int(request.GET.get("y", 0))}