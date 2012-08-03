from setuptools import setup, find_packages

setup(
    name = "amitu-d",
    description = "D, django based miniframework",
    version = "0.1.0",
    author = 'Amit Upadhyay',
    author_email = "upadhyay@gmail.com",

    url = 'http://github.com/amitu/amitu-d/',
    license = 'BSD',

    install_requires = ["fhurl", "gunicorn"],
    namespace_packages = ["amitu"],
    packages = find_packages(),

    zip_safe = True,
)
