from setuptools import setup

setup(
    name = "importd",
    description = "a django based miniframework, inspired by sinatra",
    long_description=open('README.rst', 'rt').read(),

    version = "0.1.2",
    author = 'Amit Upadhyay',
    author_email = "upadhyay@gmail.com",

    url = 'http://amitu.com/importd/',
    license = 'BSD',

    install_requires = ["fhurl", "gunicorn", "smarturls"],
    py_modules = ["importd"],

    zip_safe = True,
)
