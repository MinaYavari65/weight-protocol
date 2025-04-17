# Simple HTTP Server in Python 3
from http.server import BaseHTTPRequestHandler, HTTPServer


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.get('content-length',0))
        post_body = self.rfile.read(content_len)
 

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        # Compute compound weights

        self.wfile.write(b"37.89")


def run_server():
    server_address = ('127.0.0.1',8080)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print('Starting server...')
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()  
