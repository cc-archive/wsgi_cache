import os
import tempfile
import shutil

from webtest import TestApp

from app import app

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

    # Test for urls that end with a /
    assert caching.resource_cache_name('bar/baz/').endswith('__index.html')

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

    # Test for urls that end with a /
    os.mkdir(os.path.join(temp_dir, 'cache', 'baz'))
    file(os.path.join(
            temp_dir, 'cache', 'baz', '__index.html'), 'w').write('\n')
    assert caching.cached('baz/')

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
    caching.store('foo/bar', 'aoe')

    # the subdirectory should have been created
    assert os.path.exists(os.path.join(temp_dir, 'cache', 'foo'))
    assert os.path.exists(os.path.join(temp_dir, 'cache', 'foo', 'bar'))
    
    assert caching.cached('foo/bar')

    shutil.rmtree(temp_dir)

def test_caching_zero_size():
    """Zero-size files in cache should be ignored."""

    import wsgi_cache

    temp_dir = tempfile.mkdtemp()

    caching = wsgi_cache.CacheMiddleware(app, {'here':temp_dir}, 'cache')

    # when we start out, nothing is cached
    assert caching.cached('cache_misshap') == False

    # store the file with no data
    caching.store('cache_misshap', '')

    # verify that the zero sized cache entry is skipped
    assert caching.cached('cache_misshap') == False

    # store the file again, but with data
    caching.store('cache_misshap', 'aoe')

    # verify that the cache entry with data is fetched
    assert caching.cached('cache_misshap')

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
    # -- we "".join the response since it's returning an iterator
    assert "".join(caching.load('test')) == contents

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
    response = caching_app.get('/index.html', extra_environ={'contents':'foo'})
    assert response.status == '200 OK'
    assert response.body == 'foo'

    # make a second request; we pass in a different value for 'contents'
    # in order to verify that we're getting the cached version
    response = caching_app.get('/index.html', extra_environ={'contents':'bar'})
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
    response = caching_app.get('/index.html', extra_environ={'contents':'foo'})
    assert response.status == '200 OK'
    assert response.body == 'foo'

    # make a second request; we pass in a different value for 'contents'
    # in order to verify that this request is not cached
    response = caching_app.get('/index.html', extra_environ={'contents':'bar'})
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


def test_respect_cache_control():
    """If the response includes a Cache-Control: no-cache header, it
    will not be cached."""

    import wsgi_cache

    temp_dir = tempfile.mkdtemp()

    caching_app = TestApp(
        wsgi_cache.CacheMiddleware(app, {'here':temp_dir}, 'cache',
                                   cache_paths='/licenses')
        )
    
    # make a request that is in cache_paths, and emit cache-control
    response = caching_app.get('/licenses/by/3.0/es/',
                               extra_environ={'contents':'foo',
                                              'cc.headers':[
                ('Cache-Control', 'no-cache')]})
    assert response.status == '200 OK'
    assert response.body == 'foo'

    # repeat the request with different contents
    response = caching_app.get('/licenses/by/3.0/es/',
                               extra_environ={'contents':'bar',
                                              'cc.headers':[
                ('Cache-Control', 'no-cache')]})
    assert response.status == '200 OK'

    # check that it was not cached
    assert response.body == 'bar'

    shutil.rmtree(temp_dir)


def test_requests_with_querystring():
    """Test that requests with a querystring are not cached."""

    import wsgi_cache

    temp_dir = tempfile.mkdtemp()

    caching_app = TestApp(
        wsgi_cache.CacheMiddleware(app, {'here':temp_dir}, 'cache')
        )

    # make a first request
    response = caching_app.get('/foo?bar=1', extra_environ={'contents':'foo'})
    assert response.status == '200 OK'
    assert response.body == 'foo'

    # make a second request; we pass in a different value for 'contents'
    # in order to verify that this request is not cached
    response = caching_app.get('/foo?bar=1', extra_environ={'contents':'bar'})
    assert response.status == '200 OK'
    assert response.body == 'bar'

    shutil.rmtree(temp_dir)

def test_custom_content_type():
    """A custom content-type can be specified in the configuration,
    which will be used for cached replies."""

    import wsgi_cache

    temp_dir = tempfile.mkdtemp()

    caching_app = TestApp(
        wsgi_cache.CacheMiddleware(app, {'here':temp_dir}, 'cache',
                                   content_type='text/plain')
        )

    # make a first request
    response = caching_app.get('/foo', extra_environ={'contents':'foo'})
    assert response.status == '200 OK'
    assert response.headers['Content-type'] == 'text/test'
    assert response.body == 'foo'

    # make a second request; we should get the cached value, text/plain
    response = caching_app.get('/foo', extra_environ={'contents':'bar'})
    assert response.status == '200 OK'
    assert response.body == 'foo'
    print response.headers
    assert response.headers['Content-type'] == 'text/plain'

    shutil.rmtree(temp_dir)
    

def test_custom_directory_index():
    """
    A specific directory_index value can be supplied to the config, which
    will affect the filename portion of a directory like-url.
    """
    import wsgi_cache

    temp_dir = tempfile.mkdtemp()

    caching = wsgi_cache.CacheMiddleware(
        app, {'here':temp_dir}, 'cache',
        directory_index='__linooks__')

    caching.store('foo/bar/', 'testcontents')
    data = file(os.path.join(temp_dir, 'cache',
                             'foo/bar', '__linooks__')).read()

    assert data == 'testcontents'
