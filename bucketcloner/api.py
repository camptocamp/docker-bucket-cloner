import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from prometheus_client import core, exposition, CollectorRegistry

class API(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            self._metrics()
        else:
            self._not_found()

    def log_message(self, format, *args):
        return

    def _metrics(self):
        """Display metrics for Prometheus."""
        output = exposition.generate_latest(core.REGISTRY)

        self.send_response(200)
        self.send_header('Content-Type', exposition.CONTENT_TYPE_LATEST)
        self.end_headers()

        self.wfile.write(output)

    def _not_found(self):
        self.send_response(404)
        self.wfile.write(bytes("Not Found", 'UTF-8'))


class ThreadedHTTPServer(object):
    def __init__(self, host, port):
        self.server = HTTPServer((host, port), API)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.deamon = True

    def start(self):
        self.server_thread.start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
