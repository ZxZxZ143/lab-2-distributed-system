# Lab 2 - REST API and Message Queue Specification

## 1. System Overview

The system consists of two Flask HTTP services: a REST API on port 5000 and an in-memory message broker on port 6000. A producer sends orders to the broker, while a consumer retrieves and processes them independently.

## 2. Functional Requirements

| Endpoint | Method | Input | Output | HTTP Status |
|---|---|---|---|---|
| `/time` | GET | None | `{"server_time": "string"}` | 200 |
| `/echo` | POST | `{"message": "string"}` | `{"message": "string"}` | 200 |
| `/echo` | POST | Missing `message` | `{"error": "field 'message' is required"}` | 400 |
| `/queue/<topic>` | POST | JSON object | `{"status": "queued", "topic": "string"}` | 201 |
| `/queue/<topic>` | GET | Topic in URL | Original JSON message | 200 |
| `/queue/<topic>` | GET | Empty queue | No response body | 204 |

Messages are processed in FIFO order. The producer submits an order approximately every 1 second. The consumer simulates processing each order for 3 seconds and polls again after 2 seconds when the queue is empty.

## 3. Constraints and Non-Functional Requirements

- **Protocol:** HTTP with JSON payloads.
- **Environment:** Python 3.9+, Flask, requests; local machine.
- **Performance target:** API responses should complete within 1 second under a local test workload of up to 10 sequential requests.
- **Reliability:** Messages remain queued when the consumer is offline, provided the broker stays running.
- **Storage:** In-memory only; messages are lost when the broker restarts.
- **Security:** Intended for local testing on a trusted machine or network. No authentication or encryption is implemented.

## 4. Assumptions

- The producer, consumer and broker run on the same computer using localhost.
- Clients send valid JSON objects; the broker does not enforce a strict message schema.
- Only one broker process is used; queues are not shared across multiple processes.
- The system is a learning prototype, not a production messaging platform.
- The consumer handles one order at a time. A message is removed from the queue when retrieved, without acknowledgement or automatic redelivery.