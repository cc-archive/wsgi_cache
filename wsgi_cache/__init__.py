import os
import cPickle as pickle

class CacheMiddleware(object):
    """A WSGI Middleware class that blindly caches the results of requests
    to the disk."""

    def __init__(self, app, global_conf, cache_dir,
                 content_type='text/html',
                 cache_paths=None,
                 directory_index='__index.html'):
        self.app = app
        self.conf = global_conf
        self.content_type = content_type
        self.directory_index = directory_index

        # determine the cache dir and make sure it exists
        self.cache_dir = os.path.join(global_conf.get('here'), 
                                      os.path.normpath(cache_dir))
        if not(os.path.exists(self.cache_dir)):
            os.makedirs(self.cache_dir)

        # store the cache_paths (if any)
        if cache_paths is None:
            self.cache_paths = None
        else:
            self.cache_paths = [p.strip() for p in cache_paths.split(',')]

            # make sure the values are specified correctly
            for path in self.cache_paths:
                assert path[0] == '/'

    def resource_name(self, environ):
        """Return the resource name for the request in the provided environ."""

        # we return [1:] since PATH_INFO starts with a '/'
        return environ['PATH_INFO'][1:]

    def resource_cache_name(self, resource):
        """Return the path name to the specified resource in the cache."""
        cache_name = os.path.join(self.cache_dir, resource)
        if resource.endswith('/'):
            cache_name = os.path.join(cache_name, self.directory_index)

        return cache_name

    def cached(self, resource):
        """Return True if the specified resource is cached; the resource is
        the cache identifier."""
        cache_name = self.resource_cache_name(resource)

        return (
            os.path.exists(cache_name)
            and not os.path.isdir(cache_name))

    def store(self, resource, contents):
        """Store the resource contents in the cache."""

        cache_filename = self.resource_cache_name(resource)

        # make sure the directories exist
        if not os.path.exists(os.path.dirname(cache_filename)):
            os.makedirs(os.path.dirname(cache_filename))

        # store the response contents
        cache = file(cache_filename, 'w')
        for line in contents:
            cache.write(line)

    __setitem__ = store

    def load(self, resource):
        """Load the resource from the cache."""

        return iter(file(self.resource_cache_name(resource), 'r'))

    __getitem__ = load

    def __serve_cached(self, environ, start_response):

        identifier = self.resource_name(environ)
        response = dict(
            status = '200 OK',
            headers = [('Content-type', self.content_type)],
            )

        def sr(status, headers):
            response['status'] = status
            response['headers'] = headers
            
        # look up the page in the cache first
        if self.cached(identifier):
            response['contents'] = self.load(identifier)
        else:
            response['contents'] = self.app(environ, sr)
            if response['status'] == '200 OK':
                self.store(identifier, response['contents'])

        start_response(response['status'], response['headers'])
        return response['contents']

    def __call__(self, environ, start_response):

        # see if we should cache this page
        if environ['QUERY_STRING']:
            # we don't cache pages with a query string
            return self.app(environ, start_response)

        # see if the requested URL falls within our specified cache_paths
        if self.cache_paths:
            for cp in self.cache_paths:
                if environ['PATH_INFO'].startswith(cp):
                    return self.__serve_cached(environ, start_response)

            # cache_paths was specified and did not match
            return self.app(environ, start_response)

        return self.__serve_cached(environ, start_response)
