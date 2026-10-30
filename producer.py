"""Submit one job and poll until done; run the API and worker first."""
import argparse
import json
import time
from urllib.request import Request, urlopen


def request(url, data=None):
    body = json.dumps(data).encode() if data is not None else None
    with urlopen(Request(url, data=body, headers={'Content-Type': 'application/json'}), timeout=5) as response:
        value = json.load(response)
        print(response.status, value, flush=True)
        return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('message', nargs='?', default='Hello distributed systems')
    parser.add_argument('--url', default='http://127.0.0.1:5000')
    args = parser.parse_args()
    job = request(args.url + '/jobs', {'message': args.message})
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        state = request(args.url + '/jobs/' + job['job_id'])
        if state['status'] == 'done':
            break
        time.sleep(1)
    else:
        raise SystemExit('Polling timeout: job remains stored; check worker and database path.')
