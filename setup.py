## Copyright (c) 2009 Nathan R. Yergler, Creative Commons

from setuptools import setup

import sys
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = "wsgi_cache",
    version = "0.1.2",
    packages = ['wsgi_cache'],
    
    # scripts and dependencies
    install_requires = [
        'setuptools',
        ],

    tests_require = [
        'nose',
        'coverage',
        'WebTest',
        ],

    entry_points = """\
      [paste.filter_app_factory]
      middleware = wsgi_cache:CacheMiddleware
      """,

    # author metadata
    author = 'Nathan R. Yergler',
    author_email = 'nathan@yergler.net',
    license = 'MIT',
    description = 'WSGI middleware for caching responses to disk.',
    long_description=(
         read('README')
         + '\n' +
         'Download\n'
         '========\n'
         )

    )
