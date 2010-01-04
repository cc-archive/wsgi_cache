import os
import cPickle as pickle

class CacheMiddleware(object):
    """A WSGI Middleware class that blindly caches the results of requests
    to the disk."""

    def __init__(self, app, global_conf, cache_dir):
        self.app = app
        self.conf = global_conf

        # determine the cache dir and make sure it exists
        self.cache_dir = os.path.join(global_conf.get('here'), 
                                      os.path.normpath(cache_dir))
        if not(os.path.exists(self.cache_dir)):
            os.makedirs(self.cache_dir)

    def resource_name(self, environ):
        """Return the resource name for the request in the provided environ."""

        # we return [1:] since PATH_INFO starts with a '/'
        return ("%s?%s" % (environ['PATH_INFO'], environ['QUERY_STRING'])
                )[1:]

    def resource_cache_name(self, resource):
        """Return the path name to the specified resource in the cache."""

        return os.path.join(self.cache_dir, resource)

    def cached(self, resource):
        """Return True if the specified resource is cached; the resource is
        the cache identifier."""

        return os.path.exists(self.resource_cache_name(resource))

    def store(self, resource, contents):
        """Store the resource contents in the cache."""

        cache_filename = self.resource_cache_name(resource)

        # make sure the directories exist
        if not os.path.exists(os.path.dirname(cache_filename)):
            os.makedirs(os.path.dirname(cache_filename))

        # pickle the contents and store them
        pickle.dump(contents, file(cache_filename, 'w'))

    __setitem__ = store

    def load(self, resource):
        """Load the resource from the cache."""

        return pickle.load(file(self.resource_cache_name(resource), 'r'))

    __getitem__ = load

    def __call__(self, environ, start_response):

        identifier = self.resource_name(environ)
        response = {}

        def sr(status, headers):
            response['status'] = status
            response['headers'] = headers
            
        # look up the page in the cache first
        if self.cached(identifier):
            response = self.load(identifier)
        else:
            response['contents'] = self.app(environ, sr)
            self.store(identifier, response)

        start_response(response['status'], response['headers'])
        return response['contents']

