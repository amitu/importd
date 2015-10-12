# make sure to use importd from the repository
import os
import sys
from importd import d, s

d(
    DEBUG=True,
    LOG_LOCATION=d.dotslash("temp-log.py"),
    DEBUG_TEST=s("DEBUG")
)

if __name__ == "__main__":
    from django.conf import settings
    if settings.DEBUG_TEST == True:
        print("Test passed")
    else:
        raise Exception("Test failed")
    d.main()
