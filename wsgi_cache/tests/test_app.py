from webtest import TestApp

def test_contents():
    """You can specify the contents of the response body in requests
    to our testing application.."""
    
    from app import app
    test_app = TestApp(app)

    response = test_app.get('/foo', extra_environ={'contents':'foo'})
    assert response.body == 'foo'

    response = test_app.get('/foo', extra_environ={'contents':'bar'})
    assert response.body == 'bar'

def test_headers():
    """Response headers can be specified in the wsgi environment as
    cc.headers."""

    from app import app
    test_app = TestApp(app)

    response = test_app.get('/foo', 
                            extra_environ={'contents':'bar',
                                           'cc.headers':[
                ('Foo', 'Bar'),
                ('Cache-Control', 'Blarf')]
                                           })

    assert response.headers.get('Foo', None) == 'Bar'
    assert response.headers.get('Cache-Control', None) == 'Blarf'

