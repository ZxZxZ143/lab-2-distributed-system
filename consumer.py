"""Worker: claim, process, then acknowledge. Restart safely after a crash."""
import argparse
import time
from broker import JobStore


def process_once(store, delay=3):
    job = store.claim()
    if job is None:
        return False
    print('processing', job['job_id'], flush=True)
    time.sleep(delay)
    result = {'message': job['payload']['message'].upper()}
    accepted = store.complete(job['job_id'], job['token'], result)
    print('done' if accepted else 'lease expired; result rejected', job['job_id'], flush=True)
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='jobs.sqlite3')
    args = parser.parse_args()
    store = JobStore(args.db)
    try:
        while True:
            if not process_once(store):
                time.sleep(1)
    except KeyboardInterrupt:
        pass
