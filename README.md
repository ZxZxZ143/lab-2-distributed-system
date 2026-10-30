# Lab 2 — REST API and a Durable Local Queue

Revised laboratory work by Kurlykov Yevgeniy. A client submits text, and the API immediately returns HTTP 202 with a job_id. A separate worker converts the text to uppercase. The client observes queued -> processing -> done and retrieves the result.

## Running the application

Python 3.9+ is required. There are no third-party runtime dependencies; requirements.txt explicitly documents this.

```bash
python -m pip install -r requirements.txt
python api.py
```

In another terminal, from the same directory:

```bash
python consumer.py
```

In a third terminal:

```bash
python producer.py "Hello distributed systems"
```

To demonstrate queued, submit a job before starting the worker, then start the worker. The producer prints HTTP status codes and responses. The API is available at http://127.0.0.1:5000. GET /time and POST /echo are also supported. Ctrl+C stops the processes; jobs.sqlite3 is retained. The API and worker must use the same --db path. broker.py is the SQLite storage module and does not run as a separate server.

## Tests and supporting materials

```bash
python -m unittest -v
```

- [spec.md](spec.md): contracts, risks, parameters and requirement traceability.
- [Lab2_Report.pdf](Lab2_Report.pdf): current report.
- [test-results.txt](test-results.txt): actual automated test output, including HTTP requests.
- [DEFENSE.md](DEFENSE.md): preparation for the individual defence.
- [GIT_HISTORY.md](GIT_HISTORY.md): original history and verification command.
- screenshots/: original images from the previous implementation; they do not demonstrate the new /jobs workflow.

The revision introduces substantive changes: SQLite persistence, transactional claims, leases and acknowledgement after processing. The former /queue/orders interface is replaced by /jobs. Submit the current materials and demonstrate a live run; do not present old screenshots as evidence of the revised implementation.

This is a local educational service. Processing may be repeated; external side effects require idempotency. Authentication, TLS, distributed storage and exactly-once execution are not provided.
