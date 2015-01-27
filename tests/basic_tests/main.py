# make sure to use importd from the repository
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from importd import d

d(
    DEBUG=True,
    INSTALLED_APPS=["app", "app2", "app3"],
    mounts={"app2": "/app2/"},
    blueprints={
        "app3": "app3.views.bp",
        "app3-clone": {"blueprint": "app3.views.bp", "url_prefix": "app3-clone/"},
    },
    MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    )
)

if __name__ == "__main__":
    d.main()
