from urllib.parse import parse_qs
from cgi import parse

def app(environ, start_response):
    if environ['REQUEST_METHOD'] == 'POST':
        params = parse_qs(environ['wsgi.input'].read())
        print(params)
    elif environ['REQUEST_METHOD'] == 'GET':
        params = parse_qs(environ['QUERY_STRING'])
        print(params)
    """Simplest possible application object"""
    data = b'Hello, World!\n'
    status = '200 OK'
    response_headers = [
        ('Content-type', 'text/plain'),
        ('Content-Length', str(len(data)))
    ]
    start_response(status, response_headers)
    return iter([data])