"""Durable local queue. A lease prevents deletion before acknowledgement."""
import json
from contextlib import contextmanager
import sqlite3
import time
import uuid


class JobStore:
    def __init__(self, path='jobs.sqlite3'):
        self.path = path
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS jobs (seq INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT UNIQUE, payload TEXT, status TEXT, result TEXT, lease_until REAL, token TEXT, attempts INTEGER DEFAULT 0)')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def submit(self, payload):
        job_id = str(uuid.uuid4())
        with self.connect() as db:
            db.execute('INSERT INTO jobs(job_id,payload,status) VALUES (?,?,?)', (job_id, json.dumps(payload), 'queued'))
        return {'job_id': job_id, 'status': 'queued'}

    def get(self, job_id):
        with self.connect() as db:
            row = db.execute('SELECT * FROM jobs WHERE job_id=?', (job_id,)).fetchone()
        if row is None:
            return None
        return {'job_id': row['job_id'], 'status': row['status'], 'attempts': row['attempts'], 'result': json.loads(row['result']) if row['result'] else None}

    def claim(self, lease_seconds=30):
        now = time.time()
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute("SELECT * FROM jobs WHERE status='queued' OR (status='processing' AND lease_until<=?) ORDER BY seq LIMIT 1", (now,)).fetchone()
            if row is None:
                return None
            token = str(uuid.uuid4())
            db.execute("UPDATE jobs SET status='processing',lease_until=?,token=?,attempts=attempts+1 WHERE job_id=?", (now + lease_seconds, token, row['job_id']))
            return {'job_id': row['job_id'], 'payload': json.loads(row['payload']), 'token': token}

    def complete(self, job_id, token, result):
        with self.connect() as db:
            changed = db.execute("UPDATE jobs SET status='done',result=?,lease_until=NULL WHERE job_id=? AND status='processing' AND token=? AND lease_until>?", (json.dumps(result), job_id, token, time.time())).rowcount
        return bool(changed)
