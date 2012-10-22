from setuptools import setup

try:
    long_description=open('README.rst', 'rt').read(),
except Exception:
    long_description=""

setup(
    name = "importd",
    description = "a django based miniframework, inspired by sinatra",
    long_description=long_description,

    version = "0.1.4",
    author = 'Amit Upadhyay',
    author_email = "upadhyay@gmail.com",

    url = 'http://amitu.com/importd/',
    license = 'BSD',

    install_requires = ["fhurl", "gunicorn", "smarturls"],
    py_modules = ["importd"],

    zip_safe = True,
)
