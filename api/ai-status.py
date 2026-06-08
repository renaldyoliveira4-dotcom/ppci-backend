from http.server import BaseHTTPRequestHandler
import json, os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        api_key_set = bool(os.environ.get("ANTHROPIC_API_KEY"))
        resp = {
            "ai_enabled": api_key_set,
            "api_key_configured": api_key_set,
            "sdk_installed": True,
            "model_default": "claude-sonnet-4-6"
        }
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(resp).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
