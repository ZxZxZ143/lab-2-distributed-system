# Distributed Systems — Laboratory Works

The laboratory submissions are maintained in separate branches. Open the relevant branch for its code, setup instructions, specification and report.

| Laboratory | Branch | Contents |
|---|---|---|
| Lab 2 | [lab2](https://github.com/ZxZxZ143/lab-2-distributed-system/tree/lab2) | REST API, asynchronous jobs, HTTP 202 with job_id, status tracking, SQLite queue and worker. |
| Lab 3 | [lab3](https://github.com/ZxZxZ143/lab-2-distributed-system/tree/lab3) | Flask REST API, Docker, Docker Compose, Kubernetes deployment, scaling and recovery experiments. |

## Instructions and reports

- **Lab 2:** [README](https://github.com/ZxZxZ143/lab-2-distributed-system/blob/lab2/README.md) · [PDF report](https://github.com/ZxZxZ143/lab-2-distributed-system/blob/lab2/Lab2_Report.pdf)
- **Lab 3:** [README](https://github.com/ZxZxZ143/lab-2-distributed-system/blob/lab3/README.md) · [PDF report](https://github.com/ZxZxZ143/lab-2-distributed-system/blob/lab3/Lab3_Reflection_Report.pdf)

Each laboratory branch contains its own spec.md, screenshots/ directory and PDF report in the project root.

## Switching branches locally

After cloning the repository, fetch the branches and select the laboratory:

```bash
git fetch origin
git switch lab2
```

For Lab 3:

```bash
git switch lab3
```

Commit or stash local changes before switching branches.

## About main

This README is the entry point for both laboratories. Existing files on main reflect the earlier Lab 3 snapshot. Use the dedicated branches above for the maintained laboratory materials.
