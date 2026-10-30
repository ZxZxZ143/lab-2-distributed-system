# Preparing for the Individual Defence

The assessment noted similarities between the previous code and other submissions. Code changes do not establish authorship or remove the need for an individual defence. Disclose assistance as required and do not claim independent work without a basis.

Explain and demonstrate:

1. Why HTTP 202 means accepted rather than completed, and why job_id and a separate GET request are needed.
2. The difference between queued, processing and done. Show these states using the producer and SQLite.
3. FIFO: seq determines claim order, but multiple workers may complete jobs in a different order.
4. Acknowledgement: the result and done state are saved after processing; receiving a job does not delete it.
5. Recovery: terminate the worker during its three-second processing delay, restart it and wait for the 30-second lease to expire.
6. Tokens: an old worker cannot acknowledge a job that has already been claimed again.
7. SQLite: an atomic transaction prevents simultaneous claims of the same record; both processes use the same database file.
8. At-least-once processing: computation may be repeated; external effects require idempotency. Repeating POST creates a different job.
9. Limitations: one host, no authentication, no lease heartbeat or cleanup, and possible data loss if the database file is damaged.
10. Run the tests and explain each assertion in your own words. Reading prepared notes is not a substitute for understanding the code.
