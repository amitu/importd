# make sure to use importd from the repository
import os
import sys
from importd import d

d(
    DEBUG=True,
    LOG_LOCATION=d.dotslash("temp-log.py"),
)

if __name__ == "__main__":
    path_with_py_api = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp-log.py")
    path_wit_d = d.dotslash("temp-log.py")
    if path_with_py_api == path_wit_d:
        print("Test passed")
    else:
        raise Exception("Test failed")

    d.main()
