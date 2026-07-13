# CloudNotes Production Architecture

This document describes the current production deployment of the CloudNotes
service as it exists at the time of the incident.

## Current Topology

```text
Users
  |
  v
Single Web Server
  |
  v
Single Application Server
  |
  v
Single Database Server
```

## Deployment Notes

- All components run in a **single cloud region**.
- The **Web Server** terminates user requests and forwards them to the
  application tier.
- The **Application Server** hosts the CloudNotes business logic and connects
  directly to the database.
- The **Database Server** is a single instance holding all persistent data.

## Current State

- There is **one** web server instance.
- There is **one** application server instance.
- There is **one** database server instance.
- There is no load balancer in front of the web tier.
- There is no failover or standby for any tier.
- There are no automated database backups.
- There is no autoscaling configured for any tier.
- The entire stack is deployed in a single region.

## Traffic Flow

1. A user sends a request to the web server.
2. The web server forwards the request to the application server.
3. The application server reads from and writes to the database server.
4. The response travels back along the same path to the user.

## Review Scope

Engineers reviewing this architecture should evaluate it against production
readiness expectations for a customer-facing service, including availability,
durability, scalability, and operational resilience.
