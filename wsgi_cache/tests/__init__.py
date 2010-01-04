import os
import tempfile
import shutil

from webtest import TestApp

TESTING_STATUS = '200 OK'
TESTING_HEADERS = [('Content-Type', 'text/test')]

def app(environ, start_response):
    """A dummy app that emits sentinel values we can use for testing."""

    start_response(TESTING_STATUS, TESTING_HEADERS)

    return [environ['contents']]

def test_initialization():
    """The cache_dir will be created relative to global_conf['here'] if 
    it does not exist."""
    
    import wsgi_cache

    temp_dir = tempfile.mkdtemp()

    caching_app = TestApp(
        wsgi_cache.CacheMiddleware(app, {'here':temp_dir}, 'cache')
        )

    assert os.path.exists(os.path.join(temp_dir, 'cache'))
    assert os.path.isdir(os.path.join(temp_dir, 'cache'))

    shutil.rmtree(temp_dir)

def test_resource_cache_name():
    """Assert that resource_cache_name returns a file path under the
    cache_dir."""

    import wsgi_cache

    temp_dir = tempfile.mkdtemp()

    caching = wsgi_cache.CacheMiddleware(app, {'here':temp_dir}, 'cache')
    
    assert caching.resource_cache_name('foo').startswith(
        os.path.join(temp_dir, 'cache'))

    shutil.rmtree(temp_dir)

def test_resource_is_cached():
    """Resources are cached in plain files; if the file exists, it's cached."""

    import wsgi_cache

    temp_dir = tempfile.mkdtemp()

    caching = wsgi_cache.CacheMiddleware(app, {'here':temp_dir}, 'cache')

    # when we start out, nothing is cached
    assert caching.cached('foo') == False

    # touch the file to signal it's been cached
    file(os.path.join(temp_dir, 'cache', 'bar'), 'w').write('\n')
    assert caching.cached('bar')

    shutil.rmtree(temp_dir)

def test_cache_subdirs_are_created():
    """If a resource has a / in its filename, the appropriate subdirectory
    structure is created."""

    import wsgi_cache

    temp_dir = tempfile.mkdtemp()

    caching = wsgi_cache.CacheMiddleware(app, {'here':temp_dir}, 'cache')

    # when we start out, nothing is cached
    assert caching.cached('foo/bar') == False

    # store the file
    caching.store('foo/bar', '')

    # the subdirectory should have been created
    assert os.path.exists(os.path.join(temp_dir, 'cache', 'foo'))
    assert os.path.exists(os.path.join(temp_dir, 'cache', 'foo', 'bar'))
    
    assert caching.cached('foo/bar')

    shutil.rmtree(temp_dir)

def test_caching():
    """Cached resources are retrieved as they were created."""

    import wsgi_cache
    import hashlib
    import datetime

    # initialize our cache
    temp_dir = tempfile.mkdtemp()
    caching = wsgi_cache.CacheMiddleware(app, {'here':temp_dir}, 'cache')

    # generate some nonsense to store
    contents = hashlib.sha1(str(datetime.datetime.now())).digest()
    
    # when we start out, nothing is cached
    assert caching.cached('test') == False

    # store the file
    caching.store('test', contents)

    # assert that we can retrieve it correctly
    assert caching.load('test') == contents

    shutil.rmtree(temp_dir)

def test_app_wrapping():
    """Test that an application is wrapped correctly and that subsequent
    requests return the cached version of a resource."""

    import wsgi_cache

    temp_dir = tempfile.mkdtemp()

    caching_app = TestApp(
        wsgi_cache.CacheMiddleware(app, {'here':temp_dir}, 'cache')
        )

    # make a first request
    response = caching_app.get('/', extra_environ={'contents':'foo'})
    assert response.status == '200 OK'
    assert response.body == 'foo'

    # make a second request; we pass in a different value for 'contents'
    # in order to verify that we're getting the cached version
    response = caching_app.get('/', extra_environ={'contents':'bar'})
    assert response.status == '200 OK'
    assert response.body == 'foo'

    shutil.rmtree(temp_dir)

def test_cache_paths():
    """Test that cache paths (paths to cache instead of everything) is 
    honored."""

    import wsgi_cache

    temp_dir = tempfile.mkdtemp()

    caching_app = TestApp(
        wsgi_cache.CacheMiddleware(app, {'here':temp_dir}, 'cache',
                                   cache_paths='/licenses')
        )

    # make a first request
    response = caching_app.get('/', extra_environ={'contents':'foo'})
    assert response.status == '200 OK'
    assert response.body == 'foo'

    # make a second request; we pass in a different value for 'contents'
    # in order to verify that this request is not cached
    response = caching_app.get('/', extra_environ={'contents':'bar'})
    assert response.status == '200 OK'
    assert response.body == 'bar'


    # make a first request
    response = caching_app.get('/licenses', extra_environ={'contents':'foo'})
    assert response.status == '200 OK'
    assert response.body == 'foo'

    # make a second request; we pass in a different value for 'contents'
    # in order to verify that we're getting the cached version
    response = caching_app.get('/licenses', extra_environ={'contents':'bar'})
    assert response.status == '200 OK'
    assert response.body == 'foo'

    shutil.rmtree(temp_dir)
