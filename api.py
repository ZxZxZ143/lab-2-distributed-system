"""HTTP API for the local durable job queue (Python standard library)."""
import argparse
import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from broker import JobStore


def make_server(host, port, store):
    class Handler(BaseHTTPRequestHandler):
        def respond(self, status, body, location=None):
            data = json.dumps(body).encode() if body is not None else b''
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            if location:
                self.send_header('Location', location)
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            path = urlsplit(self.path).path
            if path == '/time':
                return self.respond(200, {'server_time': datetime.now(timezone.utc).isoformat()})
            if path.startswith('/jobs/'):
                job = store.get(path[len('/jobs/'):])
                return self.respond(200 if job else 404, job or {'error': 'job not found'})
            self.respond(404, {'error': 'route not found'})

        def do_POST(self):
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if size < 1 or size > 65536:
                    return self.respond(413 if size > 65536 else 400, {'error': 'body must be 1..65536 bytes'})
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict):
                    raise ValueError('JSON object required')
            except (ValueError, UnicodeDecodeError):
                return self.respond(400, {'error': 'valid JSON object required'})
            path = urlsplit(self.path).path
            if path in ('/echo', '/jobs'):
                message = data.get('message')
                if not isinstance(message, str) or not message.strip() or len(message) > 1000:
                    return self.respond(400, {'error': 'message must be a non-empty string of at most 1000 characters'})
                if path == '/echo':
                    return self.respond(200, {'message': message})
                job = store.submit({'message': message})
                return self.respond(202, job, '/jobs/' + job['job_id'])
            self.respond(404, {'error': 'route not found'})
    return ThreadingHTTPServer((host, port), Handler)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='jobs.sqlite3')
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()
    server = make_server('127.0.0.1', args.port, JobStore(args.db))
    print(f'API: http://127.0.0.1:{args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
