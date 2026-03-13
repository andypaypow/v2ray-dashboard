#!/usr/bin/env python3
import json
import os
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler

HOST = '0.0.0.0'
PORT = 8094
DATA_FILE = '/app/data/devices.json'

class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.data_file = DATA_FILE
        super().__init__(*args, directory='/app/public', **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        elif self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            data = self.load_data()
            self.wfile.write(json.dumps(data).encode())
            return
        elif self.path == '/api/export-all':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Disposition', 'attachment; filename=v2ray-config.json')
            self.end_headers()
            data = self.load_data()
            self.wfile.write(json.dumps(data, indent=2).encode())
            return
        super().do_GET()

    def do_POST(self):
        if self.path == '/api/save':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            self.save_devices(data.get('devices', []))
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {
            'v2ray_config': {
                'host': '72.62.181.239',
                'port_socks': 1082,
                'port_http': 1083,
                'username': 'npvuser',
                'password': 'npv1234'
            },
            'devices': []
        }

    def save_devices(self, devices):
        data = self.load_data()
        data['devices'] = devices
        data['last_updated'] = datetime.now().isoformat()
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def log_message(self, format, *args):
        print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {format % args}')

def main():
    server = HTTPServer((HOST, PORT), DashboardHandler)
    print(f'V2Ray Dashboard running on http://{HOST}:{PORT}')
    print(f'Access via: http://72.62.181.239:{PORT}')
    server.serve_forever()

if __name__ == '__main__':
    main()
