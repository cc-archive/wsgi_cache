TESTING_STATUS = '200 OK'
TESTING_HEADERS = [('Content-Type', 'text/test')]

def app(environ, start_response):
    """A dummy app that emits sentinel values we can use for testing."""

    headers = TESTING_HEADERS[:] + environ.get('cc.headers', [])
    start_response(TESTING_STATUS, headers)

    return [environ['contents']]
