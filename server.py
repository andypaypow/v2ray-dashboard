#!/usr/bin/env python3
import json
import os
import hashlib
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler

HOST = '0.0.0.0'
PORT = 8094
DATA_FILE = '/app/data/devices.json'
MAX_DEVICES = 2  # Maximum 2 appareils autorisés

def generate_short_code():
    """Generate a unique 3-character short code"""
    import random
    import string
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=3))

def short_code_to_uuid(short_code):
    """Convert short code to UUID using hash"""
    salt = "v2ray-vless-salt-2026"
    hash_input = f"{short_code}{salt}".encode('utf-8')
    hash_bytes = hashlib.sha256(hash_input).digest()[:16]
    hex_str = hash_bytes.hex()
    return f"{hex_str[0:8]}-{hex_str[8:12]}-4{hex_str[13:16]}-{hex_str[16:20]}-{hex_str[20:32]}"

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
            # Add max devices limit to response
            data['max_devices'] = MAX_DEVICES
            data['devices_count'] = len(data.get('devices', []))
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
            devices = data.get('devices', [])
            
            # Check device limit
            active_devices = [d for d in devices if self.is_device_active(d)]
            if len(active_devices) > MAX_DEVICES:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': f'Maximum {MAX_DEVICES} appareils autorisés. Vous avez {len(active_devices)} appareils actifs.'
                }).encode())
                return
            
            self.save_devices(devices)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'max_devices': MAX_DEVICES}).encode())
        elif self.path == '/api/check-code':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            short_code = data.get('code', '').upper()
            existing = self.find_device_by_short_code(short_code)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'exists': existing is not None, 'device': existing}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def is_device_active(self, device):
        """Check if a device is active (not expired)"""
        if not device.get('expiryDate'):
            return True  # No expiry = active
        expiry = datetime.fromisoformat(device['expiryDate'])
        return datetime.now().replace(tzinfo=None) < expiry.replace(tzinfo=None)

    def find_device_by_short_code(self, short_code):
        """Find device by short code"""
        data = self.load_data()
        for device in data.get('devices', []):
            if device.get('shortCode') == short_code:
                return device
        return None

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                # Convert legacy devices
                for device in data.get('devices', []):
                    if 'shortCode' not in device and 'deviceId' in device:
                        device['shortCode'] = device['deviceId'][:3].upper()
                    if 'shortCode' not in device and 'id' in device:
                        device['shortCode'] = device['id'][:3].upper()
                return data
        return {
            'v2ray_config': {
                'host': '72.62.181.239',
                'port_vless': 8443,
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
    print(f'Maximum devices: {MAX_DEVICES}')
    print(f'Access via: http://72.62.181.239:{PORT}')
    server.serve_forever()

if __name__ == '__main__':
    main()
