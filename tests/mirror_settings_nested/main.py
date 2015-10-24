# make sure to use importd from the repository
import os
import sys
from importd import d, s
try:
    d(
        DEBUG=True,
        LOG_LOCATION=d.dotslash("temp-log.py"),
        DEBUG_TEST=[s("DEBUG")]
    )
except:
    print("test passed")
else:
    raise Exception("test failed")

    
