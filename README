==========
wsgi_cache
==========

:Date: 2010-01-05
:Authors: Nathan R. Yergler <nathan@yergler.net>
:Copyright: 2010, Nathan R. Yergler, Creative Commons; 
	    licensed to the public under the MIT License.

``wsgi_cache`` is a piece of WSGI middleware that provides disk
caching for WSGI applications.  It is somewhat coarse and rather
inflexible, sort of like your grandpa.

``wsgi_cache`` is designed to cache requests to a WSGI site to disk in
a cache directory on disk.  The cache directory will have the same
directory layout as the requests (ie, if ``/foo/bar`` is requested, the
``foo`` directory will be made in the cache and ``bar`` will be stored
there).  There is *no* cache expiration beyond deleting cached files
from the disk.  This is a feature.

Installation
============

``wsgi_cache`` can be installed as a Python egg, using easy_install::

  $ easy_install wsgi_cache

Configuration
=============

Configuration of wsgi_cache will often be done using Paste Deploy.  In
this situation, it can be configured as a filter::

  [app:main]
  use = egg:my_wsgi_app#app
  filter-with = cache

  [filter:cache]
  use = egg:wsgi_cache#middleware
  cache_dir = ./cache

The ``cache_dir`` is the only required configuration parameter, and
will be interpreted as relative to ``global_conf['here']``.

``wsgi_cache`` also supports three additional configuration parameters:

* content_type
    Specifies the content type used when serving cached resources; see
    Limitations_ below for details on this.  By default this is set to
    ``text/html``.
* cache_paths
    A comma separated list of paths, starting with a ``/``, that
    specifies the paths to cache.  If specified, only requests to
    paths starting with one of these strings will be cached.
* directory_index
    When accessing a path that ends in a ``/`` (like ``/monkeys/``),
    wsgi_cache needs to create a special filename.  By default this is
    ``__index.html``.  So by default, caching the page ``/monkeys/``
    saves to the file ``${path_to_cache}/monkeys/__index.html``; if we
    set directory_index to ``dir_x`` it would save to
    ``${path_to_cache}/monkeys/dirx``.

Behavior
========

When a request comes in, ``wsgi_cache`` examines the path to determine
if it should be cached.  Requests with a querystring are **not**
cached, regardless of the use of ``cache_paths``.  If the request is
supposed to be cached, ``wsgi_cache`` looks for the page in the cache
and serves that copy, if available.  If unavailable, the request is
passed to the application and the result is saved and returned.

Note that in many situations, you'll want to exploit ``wsgi_cache``'s
on disk cache layout to serve the cached version directly using your
front end web server (ie, Apache with mod_rewrite).

Development
===========

``wsgi_cache`` may be developed using `buildout`_ ::

  $ python bootstrap.py
  $ ./bin/buildout

This will install any dependencies, as well as create a wrapper
``python`` script that can be used to run a shell with ``wsgi_cache``
on the Python path.

Running Tests
-------------

``wsgi_cache`` uses nose_ for running tests.  You can run the test
suite by running::

  $ python setup.py nosetests

If you're using buildout for development, nose will be installed in
the buildout for you::

  $ ./bin/python setup.py nosetests

Limitations
===========

* ``wsgi_cache`` only stores the response body in order to allow
  serving of the cached files by a faster, static webserver.  As such,
  it can only return a single content-type at this point.

.. _nose: http://somethingaboutorange.com/mrl/projects/nose/0.11.1/
.. _buildout: http://buildout.org/
