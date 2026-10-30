import concurrent.futures
import json
import tempfile
import threading
import time
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from pathlib import Path
from api import make_server
from broker import JobStore
from consumer import process_once


class LabTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / 'test.sqlite3')
        self.store = JobStore(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_fifo_and_ack(self):
        a = self.store.submit({'message': 'one'})
        b = self.store.submit({'message': 'two'})
        first = self.store.claim()
        self.assertEqual(first['job_id'], a['job_id'])
        self.assertEqual(self.store.get(a['job_id'])['status'], 'processing')
        self.assertFalse(self.store.complete(a['job_id'], 'wrong', {}))
        self.assertTrue(self.store.complete(a['job_id'], first['token'], {'message': 'ONE'}))
        self.assertEqual(self.store.claim()['job_id'], b['job_id'])
        self.assertFalse(self.store.complete(a['job_id'], first['token'], {}))

    def test_restart_and_expired_lease(self):
        job = self.store.submit({'message': 'retry'})
        old = self.store.claim(lease_seconds=0.01)
        time.sleep(0.02)
        restored = JobStore(self.path)
        new = restored.claim()
        self.assertEqual(new['job_id'], job['job_id'])
        self.assertNotEqual(new['token'], old['token'])
        self.assertFalse(restored.complete(job['job_id'], old['token'], {}))
        self.assertTrue(restored.complete(job['job_id'], new['token'], {'message': 'RETRY'}))
        self.assertEqual(JobStore(self.path).get(job['job_id'])['attempts'], 2)
        self.assertIsNone(restored.claim())

    def test_concurrent_claims(self):
        for n in range(12):
            self.store.submit({'message': str(n)})
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            claims = list(pool.map(lambda _: self.store.claim(), range(12)))
        self.assertEqual(len({j['job_id'] for j in claims}), 12)

    def test_http_workflow_and_validation(self):
        server = make_server('127.0.0.1', 0, self.store)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = 'http://127.0.0.1:' + str(server.server_port)
        def call(path, body=None):
            req = Request(base + path, data=body, headers={'Content-Type': 'application/json'})
            try:
                response = urlopen(req, timeout=5)
            except HTTPError as error:
                response = error
            with response:
                return response.status, json.load(response)
        try:
            self.assertEqual(call('/time')[0], 200)
            self.assertEqual(call('/echo', b'{"message":"hello"}'), (200, {'message': 'hello'}))
            for body in [b'{}', b'[]', b'null', b'bad', b'{"message":7}', b'{"message":" "}', json.dumps({'message': 'x'*1001}).encode()]:
                self.assertEqual(call('/jobs', body)[0], 400)
            self.assertEqual(call('/jobs', b'x'*65537)[0], 413)
            self.assertEqual(call('/jobs/missing')[0], 404)
            code, job = call('/jobs', b'{"message":"hello"}')
            self.assertEqual(code, 202)
            path = '/jobs/' + job['job_id']
            self.assertEqual(call(path)[1]['status'], 'queued')
            process_once(self.store, delay=0)
            done = call(path)[1]
            self.assertEqual(done['status'], 'done')
            self.assertEqual(done['result'], {'message': 'HELLO'})
            print('HTTP evidence:', code, job, done)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == '__main__':
    unittest.main(verbosity=2)
