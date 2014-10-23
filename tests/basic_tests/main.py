# make sure to use importd from the repository
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from importd import d

d(
    DEBUG=True,
    INSTALLED_APPS=["app", "app2", "app3"],
    mounts={"app2": "/app2/"},
    MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    )
)

from app3.views import bp as bp_app3
d.register_blueprint(bp_app3, url_prefix='app3/', namespace='app3', app_name='bar')

if __name__ == "__main__":
    d.main()
