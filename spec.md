# Lab 2 — Revised Implementation Specification

## Purpose and scope

Local asynchronous processing of text jobs. The HTTP API accepts a job, and a separate worker converts its message to uppercase. SQLite stores the queue, result and status. The API and worker are separate processes on one computer using one database file. Python 3.9+ and its standard library are required; AWS/SQS and external runtime dependencies are not used.

## API contract

| Request | Input | Response / status |
|---|---|---|
| GET /time | None | 200, server_time: UTC ISO 8601 string |
| POST /echo | Object containing message | 200, message: original string |
| POST /jobs | Object containing message | 202, job_id: UUID string, status: queued; Location: /jobs/{job_id} |
| GET /jobs/{job_id} | UUID in the path | 200, job_id, status, attempts: integer, result: null or an object containing message |
| GET /jobs/{unknown-id} | Unknown ID | 404, error |

message must be a string that is non-empty after stripping whitespace and contains at most 1000 characters; original whitespace is preserved. Additional fields are ignored. The JSON body must be an object; invalid JSON, types or message values produce HTTP 400. The body is limited to 65536 bytes (413 if exceeded). Unknown routes return 404. The former /queue/orders interface is replaced by /jobs.

## Queue and acknowledgement

Each record contains seq (increasing order), job_id (unique UUID), payload (JSON containing message), status, result, lease_until (Unix timestamp), token (UUID for the current claim) and attempts (claim counter). States: queued -> processing -> done. An expired processing job can be claimed again with a new token.

A BEGIN IMMEDIATE transaction selects the earliest available record and leases it for 30 seconds. The record is not deleted. Acknowledgement is accepted only for the current token before lease expiry. The result and done state are committed together. Processing takes three seconds; the worker waits one second when the queue is empty. After a worker failure, a restarted worker can claim the job after its lease expires.

FIFO applies to the claim order of available jobs. Multiple workers may finish jobs in a different order. Repeated processing is possible (at-least-once processing when workers restart); exactly-once external effects are not promised. The text transformation is deterministic and has no external side effects.

## Constraints, assumptions and risks

| Assumption / constraint | Consequence and mitigation |
|---|---|
| One computer and one SQLite path | Different paths create independent queues; run from the same directory or pass the same --db path |
| Healthy local filesystem | Ordinary process restarts retain data; file deletion or corruption causes loss; backup is outside this assignment |
| Processing takes less than 30 seconds | Long processing loses its lease; tokens reject stale acknowledgements; longer tasks need a heartbeat |
| Processing may repeat | External payments or emails require idempotency keyed by job_id |
| No authentication or TLS | The API binds to 127.0.0.1; do not expose it publicly |
| One SQLite writer | Suitable for an educational workload, not a distributed cluster; lock waiting is limited to ten seconds |
| Completed records are retained | The database grows; a cleanup policy is outside this prototype |
| Client polling has a deadline | The producer stops polling after 60 seconds; the job remains stored |

## Verifiable requirements and traceability

| Requirement | Implementation | Verification |
|---|---|---|
| 202, job_id, queued and done | api.py, broker.py, consumer.py | test_http_workflow_and_validation |
| Errors 400/404/413 | api.py | test_http_workflow_and_validation |
| FIFO and acknowledgement after processing | JobStore.claim/complete | test_fifo_and_ack |
| Database reopening and claim recovery | SQLite, lease/token | test_restart_and_expired_lease |
| No simultaneous duplicate claims for 12 jobs | BEGIN IMMEDIATE | test_concurrent_claims (six threads) |

Measurable parameters: at most 1000 message characters and 64 KiB per request body; a 30-second lease; a three-second worker delay; one-second polling; and a five-second producer HTTP timeout. These are not latency guarantees under arbitrary load. Run python -m unittest -v; actual results are recorded in test-results.txt.
