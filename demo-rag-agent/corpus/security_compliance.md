# Security & Data Compliance Policy

## 1. Data Classification & Encryption Standards
All organizational data is classified into three tiers: Public, Internal, and Highly Confidential (PII/Financial).
- **Encryption at Rest**: AES-256 encryption is mandatory across all persistent storage volumes, S3 buckets, and database tables using AWS KMS customer-managed keys (CMK) with annual key rotation.
- **Encryption in Transit**: TLS 1.3 is enforced for all external and internal RPC endpoints. TLS 1.0 and 1.1 handshakes are permanently rejected.

## 2. Access Control & Principle of Least Privilege
Access to production infrastructure requires:
- Hardware-token Multi-Factor Authentication (MFA) via WebAuthn/FIDO2.
- Ephemeral just-in-time (JIT) IAM credentials with a maximum session lifespan of 60 minutes.
- All administrative actions are recorded in immutable AWS CloudTrail audit logs streamed to a dedicated compliance S3 bucket.

## 3. Data Retention & Purge Lifecycle
Customer records and telemetry logs are governed by strict lifecycle rules:
- Operational trace telemetry is retained for 90 days before automatic deletion.
- Customer account data must be completely expunged within 30 days upon receipt of a verified GDPR/CCPA erasure request.
- Financial audit logs and invoice receipts are retained for 7 years to comply with statutory accounting requirements.
