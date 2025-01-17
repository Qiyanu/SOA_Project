from wsgiref.simple_server import make_server
from app.soap_api.services import wsgi_app

if __name__ == "__main__":
    # Run the SOAP server
    server = make_server("0.0.0.0", 8001, wsgi_app)
    print("SOAP server running on http://0.0.0.0:8001")
    server.serve_forever()
