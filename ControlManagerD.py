from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler, HTTPServer
import json
import threading

class Component:
    def __init__(self, name):
        self.name = name
        self.weight = 0.0

class Control:
    def __init__(self, id, masters, slaves, ip, port, components):
        self.id = id
        self.masters = masters # Example {'O3': '192.168.0.1',...}
        self.slaves = slaves # Example {'O1': '192.168.0.3',...}
        self.ip = ip
        self.port = port
        self.components = components

    def __str__(self):
        return f"{self.ip}:{self.port}"

def run_control_server(id, port):
    class ControlServer(BaseHTTPRequestHandler):
        def do_POST(self):
            content_len = int(self.headers.get('content-length', 0))
            post_body = self.rfile.read(content_len)
            #print(f"Received POST request with body: {post_body}")
            
            # Compute weights        
                    
            # Send a response back to the client
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

    server_address = ('', port)
    new_server = ThreadingHTTPServer(server_address, ControlServer)
    print(f"Control {id} started on port {port}")
    new_server.serve_forever()

class ControlManager(BaseHTTPRequestHandler):   
    def do_POST(self):
        # Deserialise JSON message from deployer
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_body_str = post_body.decode('utf-8')
        data = json.loads(post_body_str)

        # Start control server
        for key, value in data.items():       
            self.next_port += 1 # TODO: Warning! Test port before using it
            
            components = []
            for component in value['components']: components.append(Component(component))

            control = Control(key, value['masters'], value['slaves'], self.server.server_address[0], self.next_port, components)              
            t2 = threading.Thread(target=run_control_server, args=(control.id, control.port,))
            t2.daemon = True  # daemon thread so it won't block program exit
            t2.start()                    
                
        # Send a response back to the client
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

def run_manager_server(ip, port):
    server_address = (ip, port)
    httpd = HTTPServer(server_address, ControlManager)
    print('Starting Control Manager Server...')
    httpd.serve_forever()

if __name__ == "__main__":
    ip = '127.0.0.1'
    port = 8080
    ControlManager.next_port = port
    run_manager_server(ip, port)