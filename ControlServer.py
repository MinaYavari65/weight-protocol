from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Lock
import requests

class ControlServer(BaseHTTPRequestHandler):
    
    def do_POST(self):
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        #print(f"Received POST request with body: {post_body}")
   
        client_ip, client_port = self.client_address
        #print(f"Client IP: {client_ip}, Client Port: {client_port}")
        slave = client_ip + ":" + str(client_port)
        print(slave)
        
        # with lock:
        #     if slave in slaves:
        #         slaves[slave]['weight'] = 100
        #         slaves[slave]['count'] = 1

        # count = 0
        # for senderId, info in slaves.items():
        #     if info['count'] == 1: count += 1

        # if(count == len(slaves)): 
        #     # Send to masters
        #     print("Weights synchronysed!")
        #     #for masterId in masters:
        #         # print("Send to master: {masterId}")
                
        # Send a response back to the client
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        # # Compute weights here
        #self.wfile.write(b"37.89")

def run_server(control):
    server_address = (control.ip, control.port)
    httpd = HTTPServer(server_address, ControlServer)
    print('Starting httpd...')
    httpd.serve_forever()