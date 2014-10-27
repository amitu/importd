# -*- coding: utf-8 -*-
from setuptools import setup

try:
    long_description = open('README.rst', 'rt').read()
except Exception:
    long_description = ""

setup(
    name="importd",
    description="a django based miniframework, inspired by sinatra",
    long_description=long_description,

    version="0.3.1",
    author='Amit Upadhyay',
    author_email="upadhyay@gmail.com",

    url='https://github.com/amitu/importd',
    license='BSD',

    install_requires=[
        "fhurl>=0.1.7", "smarturls", "six", "Django>=1.3",
        "dj-database-url",
    ],
    packages=["importd"],

    zip_safe=True,
)
