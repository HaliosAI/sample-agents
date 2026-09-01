# Cloud Infrastructure & Microservices Architecture Specification

## 1. Network Topology & VPC Peering
The production environment operates within a multi-region Virtual Private Cloud (VPC) spanning `us-east-1` (Primary) and `us-west-2` (Disaster Recovery).
All internal microservice communication is routed over private VPC peering connections with zero public internet traversal.
Subnets are partitioned into:
- **Public Subnet**: Ingress Application Load Balancers (ALBs) and NAT Gateways.
- **Application Subnet (Private)**: Kubernetes (EKS) worker nodes running containerized workloads.
- **Database Subnet (Isolated)**: PostgreSQL Aurora clusters and Redis caching instances with strict security group egress rules.

## 2. Ingress & API Gateway Routing
Incoming traffic passes through AWS CloudFront CDN for edge TLS termination and DDoS mitigation before hitting the Kong API Gateway.
- Maximum request payload size is capped at 10 MB.
- Ingress rate limiting is enforced per API token: 100 requests/minute for standard tiers, and 10,000 requests/minute for enterprise tiers.
- Cross-Origin Resource Sharing (CORS) is restricted to verified customer domain origins.

## 3. Database Replication & Failover Procedures
The primary datastore is an Amazon Aurora PostgreSQL 16 cluster configured with Multi-AZ replication.
- Read replicas are provisioned across 3 availability zones with an asynchronous replication lag threshold of < 15 milliseconds.
- In the event of primary master node degradation, automatic failover is initiated by the cluster manager within 30 seconds.
- Backup snapshots are captured hourly with a 35-day point-in-time recovery (PITR) retention window.

## 4. Distributed Caching & Session Management
Redis cluster nodes (version 7.2) serve as the distributed cache layer:
- Cache eviction policy is configured to `volatile-lru` (Least Recently Used with explicit TTL).
- Session tokens expire automatically after 24 hours of inactivity.
- Cache invalidation employs pub/sub event broadcasting across all application worker pods upon entity mutation.
