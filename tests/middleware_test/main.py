# make sure to use importd from the repository
import os
import sys
from importd import d, s


d(
    DEBUG=True,
    MIDDLEWARE_CLASSES=(
        'middlewares.middleware_demo.middleware_demo',
    ),
    INSTALLED_APPS=['middlewares'],
)

@d("/", name="main")
def main(request):
    return d.HttpResponse("Middleware demo")

if __name__ == "__main__":
    d.main()
