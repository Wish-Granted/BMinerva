from cheroot.wsgi import Server
from cheroot.ssl.builtin import BuiltinSSLAdapter
from app import create_app

app = create_app()

server = Server(("0.0.0.0", 8443), app)
server.ssl_adapter = BuiltinSSLAdapter(
    r"C:\bminerva\certs\server.crt",
    r"C:\bminerva\certs\server.key",
)

if __name__ == "__main__":
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()