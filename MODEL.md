# Data Model Design Document

## Overview

The Breathe ESG Data Ingestion System uses a relational data model with PostgreSQL (SQLite for development) that supports multi-tenancy, flexible raw data storage, normalized emissions records, and an immutable audit trail.

## Design Rationale

### Multi-Tenancy Approach

We chose the **Shared Database, Shared Schema** pattern with a `client_company` foreign key on all data tables. This provides:
- Simplest operational model (single database to manage)
- Row-level isolation through Django ORM filtering
- Permission classes enforce tenant boundaries at the API layer
- Adequate for the expected scale (dozens of tenants, not thousands)

### UUID Primary Keys

All models use UUID primary keys instead of auto-incrementing integers:
- Prevents information leakage (can't guess record IDs)
- Supports distributed ID generation
- Safe for use in URLs without exposing record counts

### JSONB for Flexible Storage

Two models use JSONB fields:
- `RawDataRecord.raw_data`: Stores unparsed input in its original format
- `DataSource.configuration`: Stores parser-specific settings per client
- `ValidationRule.configuration`: Stores rule parameters

This avoids schema migrations when new source formats are added.

## Entity Relationships

```
ClientCompany (1) ──── (N) DataSource
ClientCompany (1) ──── (N) RawDataRecord
ClientCompany (1) ──── (N) NormalizedRecord
ClientCompany (1) ──── (N) ValidationRule

DataSource (1) ──── (N) RawDataRecord
RawDataRecord (1) ──── (1) NormalizedRecord

NormalizedRecord (1) ──── (N) SuspiciousFlag
NormalizedRecord (1) ──── (N) AuditTrailEvent

User (1) ──── (N) NormalizedRecord (approved_by)
User (1) ──── (N) SuspiciousFlag (dismissed_by)
User (1) ──── (N) AuditTrailEvent (user)
```

## Key Design Decisions

1. **OneToOne between RawDataRecord and NormalizedRecord**: Each raw record produces exactly one normalized record. This maintains clear lineage.

2. **Append-only AuditTrailEvent**: The model overrides `save()` and `delete()` to prevent modification after creation. This ensures audit integrity.

3. **SuspiciousFlag as separate model**: Flags are decoupled from records to support multiple flags per record and independent lifecycle management.

4. **Approval status on NormalizedRecord**: Rather than a separate approval table, the status lives on the record for query efficiency.

5. **Indexes optimized for common queries**: Composite indexes on (client_company, activity_date), (client_company, emission_scope), and (client_company, approval_status) support the dashboard's primary access patterns.
