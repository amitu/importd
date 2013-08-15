from setuptools import setup

try:
    long_description=open('README.rst', 'rt').read()
except Exception:
    long_description=""

setup(
    name = "importd",
    description = "a django based miniframework, inspired by sinatra",
    long_description=long_description,

    version = "0.2.2",
    author = 'Amit Upadhyay',
    author_email = "upadhyay@gmail.com",

    url = 'http://amitu.com/importd/',
    license = 'BSD',

    install_requires = ["fhurl>=0.1.7", "gunicorn", "smarturls", "six"],
    packages = ["importd"],

    zip_safe = True,
)
