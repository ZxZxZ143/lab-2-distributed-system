# Lab 3 - REST API, Docker and Kubernetes Specification (v2)

## 1. System Overview

This is version 2 of the Flask REST API introduced in Laboratory Work 2. The API listens on port 5000. In Lab 3, the service is packaged as a Docker image (`my-api:lab3`) and deployed to a local Kubernetes cluster with three replicas behind a single Service. The API is stateless and requires no database or external credentials.

The original Lab 2 message broker, producer and consumer may remain in the repository for reference, but **they are not deployed or tested in Lab 3**. The queue endpoints are provided by the separate `broker.py` service on port 6000, not by the containerized REST API.

## 2. API Contract - v2

| Endpoint | Method | Request | Example response | HTTP status |
|---|---|---|---|---|
| `/time` | GET | None | `{"time":"2026-10-24 18:00:00","served_by":"my-api-abc123"}` | 200 |
| `/echo` | POST | `{"message":"Hello"}` | `{"message":"Hello"}` | 200 |
| `/echo` | POST | Missing `message`, empty JSON or invalid JSON | `{"error":"field 'message' is required"}` | 400 |

**Change from v1 to v2:** `/time` returns `time` in local server time (`YYYY-MM-DD HH:MM:SS`) and adds `served_by`, the hostname of the container/pod that handled the request. The previous v1 response field `server_time` is replaced by `time`. The `/echo` contract is unchanged.

The hostname is obtained using Python `socket.gethostname()`. Under Kubernetes this identifies the responding pod; the `served_by` values can be aggregated to observe request distribution across replicas.

## 3. Container Packaging

- **Base image:** `python:3.12-slim`
- **Application path in container:** `/app/app.py`
- **Dependencies:** `flask` (installed from `requirements.txt`)
- **Listen address:** `0.0.0.0:5000`, so the container accepts network traffic
- **Docker image tag:** `my-api:lab3`
- **Docker Compose:** `docker-compose.yml` builds the image from `./app`, publishes `5000:5000`, and sets `restart: unless-stopped`

## 4. Kubernetes Deployment

- `k8s/deployment.yaml`: Deployment named `my-api` with `replicas: 3`, pod label `app: my-api`, container image `my-api:lab3`, and container port 5000.
- `k8s/service.yaml`: NodePort Service named `my-api`, selecting `app: my-api`, exposing port 80 and forwarding traffic to target port 5000.
- Local images are loaded into Minikube with `minikube image load my-api:lab3` before applying manifests.
- The Service discovers matching pods through its label selector; a single URL is used to access the replicas.
- For the lab's distribution check, send 30 independent `/time` requests through the Minikube Service URL. At least two distinct `served_by` values must appear. Uniform distribution is not required.
- For self-healing, delete one pod while the Deployment desires three replicas. Kubernetes creates a replacement, and healthy remaining pods can continue serving traffic.
- For scaling, use `kubectl scale deployment my-api --replicas=5` and then set replicas back to 3.

## 5. Constraints and Assumptions

- The API is an educational local prototype. No authentication, TLS, external storage, message queue worker, or AWS account is required for Lab 3.
- `/time` and `/echo` do not rely on per-pod persistent state, so each request can be served independently by a replica.
- Service routing does not guarantee perfectly equal distribution over a small sample of requests.
- Kubernetes replacement pod readiness and successful HTTP checks must be demonstrated with actual local execution and screenshots; the configuration alone does not prove that the experiments were run.
- Secrets and AWS keys must never be copied into the Docker image.

## 6. Legacy Lab 2 Features (not part of Lab 3 deployment)

The original `broker.py` process provides `/queue/<topic>` (POST to enqueue, GET to dequeue) on port 6000. Messages are stored in memory and follow FIFO order; a producer generates orders and a consumer polls and processes them. These components are deliberately excluded from the Lab 3 container, Deployment and Service. The Lab 2 functionality is unchanged in its original files.
