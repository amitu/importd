# -*- coding: utf-8 -*-


from setuptools import setup


try:
    with open('README.rst', "rt") as long_description_file_txt:
        long_description = long_description_file_txt.read().strip()
except Exception:
    long_description = ""


setup(
    name="importd",
    description="a django based miniframework, inspired by sinatra",
    long_description=long_description,

    version="0.2.9",
    author='Amit Upadhyay',
    author_email="upadhyay@gmail.com",

    url='https://github.com/amitu/importd',
    license='BSD',

    install_requires=[
        "fhurl>=0.1.7", "gunicorn", "smarturls", "six", "Django>=1.3",
        "dj-database-url",
    ],
    packages=["importd"],

    zip_safe=True,
)
