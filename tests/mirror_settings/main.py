# make sure to use importd from the repository
import os
import sys
from importd import d, s

d(
    DEBUG=True,
    LOG_LOCATION=d.dotslash("temp-log.py"),
    DEBUG_TEST=s("DEBUG"), 
    INSTALLED_APPS=["test_app"],
)

if __name__ == "__main__":
    from django.conf import settings
    assert settings.DEBUG_TEST
    d.main()
