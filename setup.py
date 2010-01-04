## Copyright (c) 2009 Nathan R. Yergler, Creative Commons

from setuptools import setup, find_packages

import sys

setup(
    name = "wsgi_cache",
    version = "0.1",
    packages = ['wsgi_cache'],
    
    # scripts and dependencies
    install_requires = [
        'setuptools',
        'nose',
        'coverage',
        'WebTest',
        ],

    # author metadata
    author = 'Nathan R. Yergler',
    author_email = 'nathan@creativecommons.org',
    description = '',
    license = 'MIT',
    url = 'http://creativecommons.org',
    entry_points = """\
      [paste.filter_app_factory]
      middleware = wsgi_cache:CacheMiddleware
      """
    )
