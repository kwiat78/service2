#!/usr/bin/env python
from pip.req import parse_requirements
from setuptools import setup
import pip

install_reqs = parse_requirements('./wsgi/requierments.txt', session=pip.download.PipSession())
reqs = [str(ir.req) for ir in install_reqs]

setup(
    # GETTING-STARTED: set your app name:
    name='django_rss',
    # GETTING-STARTED: set your app version:
    version='1.0',
    # GETTING-STARTED: set your app description:
    description='OpenShift App',
    # GETTING-STARTED: set author name (your name):
    author='Your Name',
    # GETTING-STARTED: set author email (your email):
    author_email='example@example.com',
    # GETTING-STARTED: set author url (your url):
    url='http://www.python.org/sigs/distutils-sig/',
    # GETTING-STARTED: define required django version:
    install_requires=reqs,
    dependency_links=[
        'https://pypi.python.org/simple/django/'
    ],
)
