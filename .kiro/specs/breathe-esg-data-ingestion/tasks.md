# Implementation Plan: Breathe ESG Data Ingestion System

## Overview

This implementation plan breaks down the Breathe ESG Data Ingestion System into discrete, sequential coding tasks. The system is a Django REST API with React frontend that consolidates emissions data from heterogeneous sources (SAP, Green Button, Concur), normalizes the data, detects quality issues, and provides an approval workflow for ESG analysts. The implementation follows a bottom-up approach: database models → business logic → API endpoints → frontend components → testing → deployment.

## Tasks

- [ ] 1. Set up Django project structure and core configuration
  - Create Django project with REST framework
  - Configure PostgreSQL database connection
  - Set up environment variable management (.env file)
  - Configure CORS for React frontend
  - Create initial Django apps: `ingestion`, `normalization`, `approval`, `audit`
  - Set up static files configuration for React build
  - _Requirements: 12.2, 12.3, 12.4_

- [ ] 2. Implement Django models and database schema
  - [ ] 2.1 Create ClientCompany model with UUID primary key
    - Implement model with name, created_at, audit_lock_date fields
    - Add database indexes on name field
    - _Requirements: 3.1, 3.4_

  - [ ] 2.2 Create DataSource model with source type choices
    - Implement model with client_company FK, source_type, name, configuration JSONB
    - Add database indexes on (client_company, source_type)
    - _Requirements: 1.6, 3.4_

  - [ ] 2.3 Create RawDataRecord model for unparsed data storage
    - Implement model with client_company FK, data_source FK, raw_data JSONB, parsing_status
    - Add database indexes on (client_company, ingestion_timestamp) and (data_source, parsing_status)
    - _Requirements: 1.4, 1.5_

  - [ ] 2.4 Create NormalizedRecord model with emission scope and approval status
    - Implement model with all normalized fields (activity_date, emission_scope, quantity, unit, etc.)
    - Add source attribution fields (original_quantity, original_unit, conversion_factor)
    - Add approval workflow fields (approval_status, approved_by, approved_at)
    - Add database indexes on (client_company, activity_date), (client_company, emission_scope), (client_company, approval_status)
    - _Requirements: 4.1, 4.2, 4.7, 5.1, 8.2_

  - [ ] 2.5 Create SuspiciousFlag model for data quality issues
    - Implement model with record FK, flag_type choices, description, status, dismissal fields
    - Add database indexes on (record, status)
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [ ] 2.6 Create AuditTrailEvent model for immutable audit log
    - Implement model with record FK, action_type choices, user FK, timestamp, field changes
    - Add database indexes on (record, timestamp) and (user, timestamp)
    - Configure model as append-only with Meta ordering
    - _Requirements: 9.1, 9.2, 9.5, 9.7_

  - [ ] 2.7 Create ValidationRule model for configurable validation
    - Implement model with client_company FK, rule_type choices, field_name, configuration JSONB
    - Add database indexes on (client_company, is_active)
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

  - [ ] 2.8 Create and apply database migrations
    - Generate Django migrations for all models
    - Apply migrations to create database schema
    - Verify all indexes are created correctly
    - _Requirements: 12.7_

- [ ] 3. Implement authentication and authorization
  - [ ] 3.1 Configure Django REST Framework token authentication
    - Set up TokenAuthentication in DRF settings
    - Create user registration and login endpoints
    - Implement token generation on login
    - _Requirements: 14.1_

  - [ ] 3.2 Create custom permission classes for tenant isolation
    - Implement IsTenantAuthorized permission class
    - Check user's authorized client_company against request data
    - _Requirements: 3.2, 3.3, 14.4_

  - [ ] 3.3 Create role-based permission classes
    - Implement IsAnalyst and IsAdministrator permission classes
    - Restrict approval actions to Analyst role or higher
    - _Requirements: 14.2, 14.3_

  - [ ]* 3.4 Write unit tests for authentication and authorization
    - Test token authentication with valid/invalid tokens
    - Test tenant isolation permission checks
    - Test role-based permission enforcement
    - _Requirements: 14.1, 14.2, 14.3, 14.4_

- [ ] 4. Implement data ingestion parsers
  - [ ] 4.1 Create SAP IDoc parser
    - Implement parser for SAP IDoc XML format (EDI_DC40 control record, hierarchical segments)
    - Extract material number, quantity, unit, cost center, transaction date
    - Handle parsing errors gracefully with descriptive error messages
    - _Requirements: 1.1_

  - [ ] 4.2 Create SAP CSV parser
    - Implement parser for SAP CSV exports with configurable column mappings
    - Support client-specific field mappings via DataSource.configuration
    - Handle missing columns and data type mismatches
    - _Requirements: 1.1, 10.4_

  - [ ] 4.3 Create Green Button XML parser
    - Implement parser for Green Button Atom/ESPI format
    - Extract UsagePoint, MeterReading, IntervalBlock, ReadingType elements
    - Parse time-series usage data with timestamps
    - _Requirements: 1.2_

  - [ ] 4.4 Create Concur API JSON parser
    - Implement parser for Concur trip data JSON format
    - Extract trip segments with travel mode, origin/destination, distance, emissions
    - Handle nested trip segment structures
    - _Requirements: 1.3_

  - [ ] 4.5 Create format router to dispatch to appropriate parser
    - Inspect request content-type and payload structure
    - Route to SAP, Green Button, or Concur parser
    - Return parsing errors for unrecognized formats
    - _Requirements: 1.1, 1.2, 1.3_

  - [ ]* 4.6 Write property test for parser format compliance
    - **Property 1: Parser Format Compliance**
    - **Validates: Requirements 1.1, 1.2, 1.3**
    - Generate random valid inputs for each format
    - Verify successful parsing without errors

  - [ ]* 4.7 Write property test for raw data preservation
    - **Property 2: Raw Data Preservation**
    - **Validates: Requirements 1.4**
    - Generate random input data
    - Verify raw_data field contains exact original input

  - [ ]* 4.8 Write property test for parsing failure handling
    - **Property 3: Parsing Failure Handling**
    - **Validates: Requirements 1.5**
    - Generate random malformed inputs
    - Verify failure record creation with error message

- [ ] 5. Implement normalization engine
  - [ ] 5.1 Create unit conversion registry and converter
    - Implement conversion factor registry for volume, energy, distance, mass units
    - Create UnitConverter class with convert() method
    - Support client-specific conversions via DataSource.configuration
    - Handle unknown units and ambiguous conversions
    - _Requirements: 4.1, 4.3_

  - [ ] 5.2 Create emission scope classifier
    - Implement ScopeClassifier with rule-based logic
    - Map activity types to Scope 1 (fuel combustion, refrigerants)
    - Map activity types to Scope 2 (purchased electricity, steam)
    - Map activity types to Scope 3 (travel, procurement, waste)
    - Flag ambiguous cases for manual review
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ] 5.3 Create normalization orchestrator
    - Implement NormalizationEngine that coordinates conversion and classification
    - Extract fields from raw data based on source type
    - Apply unit conversion and preserve original values
    - Apply scope classification
    - Standardize date formats to ISO 8601
    - Create NormalizedRecord with all fields populated
    - _Requirements: 4.1, 4.2, 4.4, 4.5, 4.6, 4.7_

  - [ ]* 5.4 Write property test for unit conversion correctness
    - **Property 7: Unit Conversion Correctness**
    - **Validates: Requirements 4.1**
    - Generate random quantities and units with known conversions
    - Verify normalized quantity equals original * conversion_factor

  - [ ]* 5.5 Write property test for normalization round-trip preservation
    - **Property 8: Normalization Round-Trip Preservation**
    - **Validates: Requirements 4.2, 4.7**
    - Generate random normalized records
    - Verify original_quantity = quantity / conversion_factor

  - [ ]* 5.6 Write property test for conversion failure flagging
    - **Property 9: Conversion Failure Flagging**
    - **Validates: Requirements 4.3**
    - Generate records with unknown/ambiguous units
    - Verify SuspiciousFlag creation with CONVERSION_FAILURE type

  - [ ]* 5.7 Write property test for scope classification
    - **Property 11, 12, 13: Scope 1/2/3 Classification**
    - **Validates: Requirements 5.1, 5.2, 5.3**
    - Generate records with various activity types
    - Verify correct emission_scope assignment

- [ ] 6. Implement validation and anomaly detection
  - [ ] 6.1 Create validation rule engine
    - Implement ValidationEngine that applies rules from ValidationRule model
    - Support numeric range validation (min/max)
    - Support required field validation
    - Support date range validation
    - Support enumerated value validation
    - Create SuspiciousFlag for each rule violation
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.6_

  - [ ] 6.2 Create anomaly detector with z-score analysis
    - Implement AnomalyDetector that calculates z-scores
    - Query historical approved records for (client_company, activity_type, unit)
    - Calculate mean and standard deviation
    - Flag records with |z-score| > 3
    - Require minimum 30 historical records before applying
    - Handle edge case where σ = 0
    - _Requirements: 7.1_

  - [ ] 6.3 Implement additional heuristic checks
    - Implement missing required field detection
    - Implement invalid date range detection (future dates, >5 years past)
    - Implement duplicate record detection based on (data_source, source_identifier, activity_date)
    - _Requirements: 7.2, 7.3, 7.5_

  - [ ]* 6.4 Write property test for statistical outlier detection
    - **Property 14: Statistical Outlier Detection**
    - **Validates: Requirements 7.1**
    - Generate historical baseline and outlier values
    - Verify OUTLIER flag creation for |z| > 3

  - [ ]* 6.5 Write property test for required field validation
    - **Property 15: Required Field Validation**
    - **Validates: Requirements 7.2**
    - Generate records with missing required fields
    - Verify MISSING_FIELD flag creation

  - [ ]* 6.6 Write property test for duplicate detection
    - **Property 16: Duplicate Detection**
    - **Validates: Requirements 7.5**
    - Generate duplicate records
    - Verify DUPLICATE flag creation for second record

- [ ] 7. Implement audit trail service
  - [ ] 7.1 Create AuditTrailService for event logging
    - Implement log_create(), log_update(), log_approve(), log_flag() methods
    - Capture timestamp, user, record, field changes, justification
    - Ensure append-only behavior (no updates/deletes)
    - _Requirements: 9.1, 9.2, 9.5, 9.7_

  - [ ] 7.2 Integrate audit logging into model save/update operations
    - Override NormalizedRecord.save() to log CREATE and UPDATE events
    - Log field-level changes with old_value and new_value
    - _Requirements: 9.1, 9.7_

  - [ ]* 7.3 Write property test for modification audit trail
    - **Property 20: Modification Audit Trail**
    - **Validates: Requirements 9.1, 9.7**
    - Generate random field modifications
    - Verify AuditTrailEvent creation with correct field changes

  - [ ]* 7.4 Write property test for audit trail immutability
    - **Property 21: Audit Trail Immutability**
    - **Validates: Requirements 9.5**
    - Attempt to modify/delete AuditTrailEvent records
    - Verify operations are rejected

- [ ] 8. Checkpoint - Ensure core business logic tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Implement data ingestion API endpoints
  - [ ] 9.1 Create POST /api/v1/ingest/sap/ endpoint
    - Accept multipart/form-data file upload or application/json
    - Validate X-Tenant-ID header
    - Route to SAP parser (IDoc or CSV based on content)
    - Store raw data in RawDataRecord
    - Trigger normalization task
    - Return 201 with ingestion job ID or 400 with errors
    - _Requirements: 1.1, 1.4, 1.6_

  - [ ] 9.2 Create POST /api/v1/ingest/greenbutton/ endpoint
    - Accept application/xml with Green Button Atom feed
    - Validate X-Tenant-ID header
    - Route to Green Button parser
    - Store raw XML in RawDataRecord
    - Trigger normalization task
    - Return 201 with job ID or 400 with errors
    - _Requirements: 1.2, 1.4, 1.6_

  - [ ] 9.3 Create POST /api/v1/ingest/concur/ endpoint
    - Accept application/json with Concur trip data
    - Validate X-Tenant-ID header
    - Route to Concur parser
    - Store raw JSON in RawDataRecord
    - Trigger normalization task
    - Return 201 with job ID or 400 with errors
    - _Requirements: 1.3, 1.4, 1.6_

  - [ ]* 9.4 Write property test for source attribution completeness
    - **Property 4: Source Attribution Completeness**
    - **Validates: Requirements 1.6, 9.2**
    - Generate random ingestion requests
    - Verify non-null data_source, ingestion_timestamp, raw_record reference

- [ ] 10. Implement data retrieval API endpoints
  - [ ] 10.1 Create GET /api/v1/records/ endpoint with filtering and pagination
    - Accept query params: tenant_id, source_type, start_date, end_date, scope, status, page, page_size
    - Apply tenant authorization filter
    - Return paginated list with summary fields
    - _Requirements: 6.1, 11.2_

  - [ ] 10.2 Create GET /api/v1/records/{id}/ endpoint
    - Enforce tenant authorization
    - Return full record details (normalized, raw, source attribution, validation, audit trail)
    - Return 404 for unauthorized or non-existent records
    - _Requirements: 6.5, 11.2_

  - [ ] 10.3 Create GET /api/v1/records/suspicious/ endpoint
    - Accept query params: tenant_id, flag_type, page, page_size
    - Return paginated list of flagged records
    - _Requirements: 6.3, 11.3_

  - [ ] 10.4 Create GET /api/v1/records/{id}/audit-trail/ endpoint
    - Return chronological list of audit events for record
    - Enforce tenant authorization
    - _Requirements: 6.6, 9.6, 11.6_

  - [ ]* 10.5 Write property test for tenant isolation
    - **Property 6: Tenant Isolation**
    - **Validates: Requirements 3.2, 3.3, 14.4**
    - Generate records for multiple tenants
    - Verify queries return only authorized tenant's records

  - [ ]* 10.6 Write unit tests for API endpoint responses
    - Test pagination, filtering, sorting
    - Test error responses (400, 401, 403, 404)
    - Test response format compliance
    - _Requirements: 11.2, 11.3, 11.6, 11.8_

- [ ] 11. Implement approval workflow API endpoints
  - [ ] 11.1 Create POST /api/v1/records/{id}/approve/ endpoint
    - Accept optional justification in request body
    - Check for unresolved SuspiciousFlags
    - Set approval_status='APPROVED', approved_by, approved_at
    - Lock core fields from modification
    - Log APPROVE event in audit trail
    - Return 200 with updated record or 400 if unresolved flags exist
    - _Requirements: 8.1, 8.2, 8.3, 8.5, 8.6, 11.4_

  - [ ] 11.2 Create POST /api/v1/records/bulk-approve/ endpoint
    - Accept array of record_ids and optional justification
    - Approve records atomically in transaction
    - Skip records with unresolved flags unless force flag set
    - Return 200 with count of approved records or 400 with failure list
    - _Requirements: 8.4, 11.4_

  - [ ] 11.3 Create POST /api/v1/records/{id}/unapprove/ endpoint
    - Accept required justification in request body
    - Check audit_lock_date constraint
    - Revert approval_status to PENDING
    - Unlock core fields
    - Log UNAPPROVE event in audit trail
    - Return 200 or 403 if past lock date
    - _Requirements: 8.7, 11.4_

  - [ ] 11.4 Create POST /api/v1/records/{id}/dismiss-flag/ endpoint
    - Accept flag_id and required justification
    - Set flag status='DISMISSED'
    - Record dismissal user and timestamp
    - Log FLAG_DISMISS event in audit trail
    - Return 200 with updated record
    - _Requirements: 7.6, 11.5_

  - [ ]* 11.5 Write property test for approval state transition
    - **Property 17: Approval State Transition**
    - **Validates: Requirements 8.2**
    - Generate random approval requests
    - Verify status, approved_by, approved_at, audit event creation

  - [ ]* 11.6 Write property test for approved record immutability
    - **Property 18: Approved Record Immutability**
    - **Validates: Requirements 8.3**
    - Attempt to modify approved records
    - Verify modifications are rejected

  - [ ]* 11.7 Write property test for flag resolution requirement
    - **Property 19: Flag Resolution Requirement**
    - **Validates: Requirements 8.5**
    - Generate records with active flags
    - Verify approval fails without force flag

- [ ] 12. Implement statistics and reporting API endpoints
  - [ ] 12.1 Create GET /api/v1/statistics/summary/ endpoint
    - Accept query params: tenant_id, start_date, end_date
    - Aggregate counts: total, failed, suspicious, approved, pending
    - Return 200 with summary statistics
    - _Requirements: 6.7, 11.7_

  - [ ] 12.2 Create GET /api/v1/statistics/by-scope/ endpoint
    - Accept query params: tenant_id, start_date, end_date
    - Group records by emission_scope
    - Return counts for Scope 1, 2, 3
    - _Requirements: 6.7, 11.7_

  - [ ]* 12.3 Write unit tests for statistics endpoints
    - Test aggregation accuracy
    - Test date range filtering
    - Test tenant isolation in statistics
    - _Requirements: 11.7_

- [ ] 13. Implement health check and monitoring endpoints
  - [ ] 13.1 Create GET /api/health/ endpoint
    - Check database connectivity
    - Return 200 with status, database, timestamp
    - _Requirements: 12.6_

  - [ ]* 13.2 Write unit tests for health check endpoint
    - Test healthy state response
    - Test database connection failure handling
    - _Requirements: 12.6_

- [ ] 14. Checkpoint - Ensure all API endpoint tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 15. Set up React frontend project structure
  - [ ] 15.1 Create React app with TypeScript
    - Initialize React project with Create React App or Vite
    - Configure TypeScript
    - Set up folder structure: components/, services/, hooks/, types/
    - Install dependencies: axios, react-query, react-router-dom
    - _Requirements: 12.3_

  - [ ] 15.2 Create TypeScript type definitions
    - Define Record, Flag, AuditEvent, DataSource, ClientCompany types
    - Match Django model field types
    - _Requirements: 6.1, 6.3, 6.6_

  - [ ] 15.3 Create API service layer with Axios
    - Implement api.ts with Axios client and auth interceptor
    - Implement recordsService.ts with CRUD operations
    - Implement approvalService.ts with approval workflow calls
    - Implement statisticsService.ts with statistics calls
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7_

- [ ] 16. Implement React dashboard components
  - [ ] 16.1 Create RecordTable component with sorting and filtering
    - Display paginated list of records
    - Support column sorting
    - Display status badges (pending, approved, flagged)
    - Handle row selection for bulk actions
    - _Requirements: 6.1_

  - [ ] 16.2 Create FilterPanel component
    - Implement date range picker
    - Implement source type dropdown
    - Implement emission scope dropdown
    - Implement approval status dropdown
    - Sync filters with URL query params
    - _Requirements: 6.4_

  - [ ] 16.3 Create SummaryStats component
    - Display statistics cards (total, failed, suspicious, approved, pending)
    - Fetch data from statistics API
    - Update on filter changes
    - _Requirements: 6.7_

  - [ ] 16.4 Create BulkActions component
    - Implement bulk approval button
    - Show confirmation modal with selected record count
    - Handle bulk approval API call
    - Display success/error messages
    - _Requirements: 8.4_

  - [ ]* 16.5 Write unit tests for dashboard components
    - Test RecordTable rendering and sorting
    - Test FilterPanel state management
    - Test SummaryStats data display
    - Test BulkActions confirmation flow
    - _Requirements: 6.1, 6.4, 6.7, 8.4_

- [ ] 17. Implement React record detail components
  - [ ] 17.1 Create RecordDetailView component
    - Display full record details in tabbed interface
    - Fetch record data from API
    - Handle loading and error states
    - _Requirements: 6.5_

  - [ ] 17.2 Create NormalizedDataPanel component
    - Display all normalized fields in readable format
    - Show emission scope badge
    - Show approval status badge
    - _Requirements: 6.5_

  - [ ] 17.3 Create RawDataPanel component
    - Display raw JSON data with syntax highlighting
    - Implement collapsible JSON tree view
    - _Requirements: 6.5_

  - [ ] 17.4 Create AuditTrailPanel component
    - Display chronological timeline of audit events
    - Show user, timestamp, action type, field changes
    - Implement infinite scroll or pagination
    - _Requirements: 6.6_

  - [ ] 17.5 Create FlagsPanel component
    - Display list of suspicious flags
    - Show flag type, description, status
    - Implement dismiss flag action with justification input
    - _Requirements: 6.3, 7.6_

  - [ ]* 17.6 Write unit tests for record detail components
    - Test RecordDetailView data fetching
    - Test NormalizedDataPanel field display
    - Test RawDataPanel JSON rendering
    - Test AuditTrailPanel timeline display
    - Test FlagsPanel dismiss action
    - _Requirements: 6.3, 6.5, 6.6, 7.6_

- [ ] 18. Implement React approval components
  - [ ] 18.1 Create ApprovalButton component
    - Implement single record approval action
    - Show confirmation dialog if unresolved flags exist
    - Handle approval API call
    - Update record status on success
    - _Requirements: 8.1, 8.6_

  - [ ] 18.2 Create BulkApprovalModal component
    - Display selected record count
    - Show warning if any records have unresolved flags
    - Implement force approval checkbox
    - Handle bulk approval API call
    - Display results (success count, failure list)
    - _Requirements: 8.4, 8.6_

  - [ ] 18.3 Create UnapprovalModal component
    - Require justification text input
    - Check audit lock date constraint
    - Handle unapproval API call
    - Display success/error messages
    - _Requirements: 8.7_

  - [ ]* 18.4 Write unit tests for approval components
    - Test ApprovalButton confirmation flow
    - Test BulkApprovalModal force approval logic
    - Test UnapprovalModal justification requirement
    - _Requirements: 8.1, 8.4, 8.6, 8.7_

- [ ] 19. Implement React routing and navigation
  - [ ] 19.1 Set up React Router with routes
    - Create routes: /dashboard, /records/:id, /login
    - Implement protected route wrapper for authentication
    - _Requirements: 14.1_

  - [ ] 19.2 Create navigation header component
    - Display user info and logout button
    - Show current tenant/client company
    - Implement navigation links
    - _Requirements: 14.1_

  - [ ]* 19.3 Write unit tests for routing and navigation
    - Test route protection for unauthenticated users
    - Test navigation link functionality
    - _Requirements: 14.1_

- [ ] 20. Checkpoint - Ensure frontend components render correctly
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 21. Set up property-based testing framework
  - [ ] 21.1 Install and configure Hypothesis for Python
    - Add hypothesis to requirements.txt
    - Configure Hypothesis settings (min 100 iterations per test)
    - Create custom strategies for domain types (quantities, units, dates, tenant IDs)
    - _Requirements: All property tests_

  - [ ] 21.2 Create Hypothesis strategies for data generation
    - Implement strategy for SAP IDoc XML generation
    - Implement strategy for Green Button XML generation
    - Implement strategy for Concur JSON generation
    - Implement strategy for random quantities, units, dates
    - Implement strategy for tenant IDs and user IDs
    - _Requirements: All property tests_

  - [ ]* 21.3 Write property test for tenant association invariant
    - **Property 5: Tenant Association Invariant**
    - **Validates: Requirements 3.1**
    - Generate random record creation requests
    - Verify non-null client_company_id on all records

  - [ ]* 21.4 Write property test for date format standardization
    - **Property 10: Date Format Standardization**
    - **Validates: Requirements 4.4**
    - Generate random date formats
    - Verify conversion to ISO 8601 format

  - [ ]* 21.5 Write property test for authentication enforcement
    - **Property 22: Authentication Enforcement**
    - **Validates: Requirements 14.1**
    - Test all protected endpoints without auth token
    - Verify 401 Unauthorized responses

  - [ ]* 21.6 Write property test for validation rule enforcement
    - **Property 23: Validation Rule Enforcement**
    - **Validates: Requirements 15.6**
    - Generate records violating various validation rules
    - Verify VALIDATION_RULE flag creation

- [ ] 22. Create comprehensive integration tests
  - [ ]* 22.1 Write integration test for full ingestion pipeline
    - Test end-to-end flow: ingest → parse → normalize → validate → flag
    - Verify RawDataRecord, NormalizedRecord, SuspiciousFlag creation
    - _Requirements: 1.1, 1.2, 1.3, 4.1, 7.1_

  - [ ]* 22.2 Write integration test for approval workflow
    - Test sequence: create record → flag → dismiss flag → approve → unapprove
    - Verify audit trail completeness
    - _Requirements: 8.1, 8.2, 8.7, 9.1_

  - [ ]* 22.3 Write integration test for multi-tenancy isolation
    - Create records for multiple tenants
    - Verify cross-tenant access attempts fail
    - Verify statistics are tenant-isolated
    - _Requirements: 3.2, 3.3, 14.4_

  - [ ]* 22.4 Write integration test for bulk operations
    - Test bulk approval with mixed valid/invalid records
    - Verify atomic transaction behavior
    - _Requirements: 8.4_

- [ ] 23. Create documentation files
  - [ ] 23.1 Create MODEL.md document
    - Document data model design rationale
    - Explain entity relationships
    - Describe JSONB field usage for flexibility
    - Explain multi-tenancy approach
    - _Requirements: 13.1_

  - [ ] 23.2 Create DECISIONS.md document
    - List ambiguity resolutions made during implementation
    - Document product management questions and answers
    - Explain scope classification edge cases
    - Document validation rule defaults
    - _Requirements: 13.2_

  - [ ] 23.3 Create TRADEOFFS.md document
    - Document three features deliberately not built
    - Justify each omission with reasoning
    - Examples: real-time ingestion, advanced ML anomaly detection, custom report builder
    - _Requirements: 13.3_

  - [ ] 23.4 Create SOURCES.md document
    - Document SAP format research with sample data
    - Document Green Button standard research with references
    - Document Concur API research with sample responses
    - Include links to official documentation
    - _Requirements: 13.4_

  - [ ] 23.5 Create README.md with setup and deployment instructions
    - Document local development setup
    - Document environment variable configuration
    - Document API endpoint documentation
    - Document deployment steps for cloud platform
    - Include sample API requests with curl examples
    - _Requirements: 13.5_

- [ ] 24. Configure deployment for production
  - [ ] 24.1 Set up environment variable management
    - Create .env.example file with all required variables
    - Document DATABASE_URL, SECRET_KEY, ALLOWED_HOSTS, CORS_ORIGINS
    - Implement environment variable loading in Django settings
    - _Requirements: 12.2_

  - [ ] 24.2 Configure PostgreSQL database for production
    - Set up PostgreSQL connection with environment variables
    - Configure connection pooling
    - Set up database backup strategy
    - _Requirements: 12.4_

  - [ ] 24.3 Configure static file serving for React frontend
    - Build React app for production
    - Configure Django to serve React build files
    - Set up static file collection
    - _Requirements: 12.3_

  - [ ] 24.4 Configure HTTPS and security settings
    - Enable HTTPS enforcement in Django settings
    - Configure SECURE_SSL_REDIRECT, SECURE_HSTS_SECONDS
    - Set up CORS headers for frontend
    - Configure CSRF protection
    - _Requirements: 12.5_

  - [ ] 24.5 Create deployment configuration for cloud platform
    - Create Procfile or equivalent for Render/Railway/Fly.io
    - Configure web server (Gunicorn)
    - Set up database migration command in deployment
    - Configure health check endpoint
    - _Requirements: 12.1, 12.6, 12.7_

  - [ ]* 24.6 Write deployment verification tests
    - Test health check endpoint returns 200
    - Test static files are served correctly
    - Test database migrations apply successfully
    - _Requirements: 12.6, 12.7_

- [ ] 25. Perform end-to-end testing and validation
  - [ ]* 25.1 Test complete user workflow
    - Test user login and authentication
    - Test data ingestion from all three sources
    - Test dashboard filtering and sorting
    - Test record detail view with all panels
    - Test flag dismissal workflow
    - Test approval workflow
    - Test audit trail display
    - _Requirements: All user stories_

  - [ ]* 25.2 Test error handling and edge cases
    - Test malformed input handling
    - Test unauthorized access attempts
    - Test concurrent approval attempts
    - Test database connection failures
    - _Requirements: 11.8_

  - [ ]* 25.3 Perform security testing
    - Test SQL injection prevention
    - Test XSS prevention in frontend
    - Test authentication bypass attempts
    - Test authorization bypass attempts
    - _Requirements: 14.1, 14.2, 14.3, 14.4_

- [ ] 26. Final checkpoint - Complete system validation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties using Hypothesis
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end workflows
- The implementation uses Python with Django REST Framework for backend and TypeScript with React for frontend
- Property-based tests require minimum 100 iterations per test for comprehensive coverage
- All property tests include comments referencing design document properties
- Authentication uses Django REST Framework TokenAuthentication
- Multi-tenancy uses shared database with tenant identifier filtering
- Database migrations must be applied before any API endpoints are implemented
- Audit trail service must be implemented before approval workflow endpoints
- React frontend components depend on API endpoints being complete

## Task Dependency Graph

```json
{
  "waves": [
    {
      "id": 0,
      "tasks": ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7"]
    },
    {
      "id": 1,
      "tasks": ["2.8", "3.1"]
    },
    {
      "id": 2,
      "tasks": ["3.2", "3.3", "4.1", "4.2", "4.3", "4.4"]
    },
    {
      "id": 3,
      "tasks": ["3.4", "4.5", "5.1", "5.2"]
    },
    {
      "id": 4,
      "tasks": ["4.6", "4.7", "4.8", "5.3", "6.1", "6.2", "6.3"]
    },
    {
      "id": 5,
      "tasks": ["5.4", "5.5", "5.6", "5.7", "6.4", "6.5", "6.6", "7.1"]
    },
    {
      "id": 6,
      "tasks": ["7.2", "9.1", "9.2", "9.3"]
    },
    {
      "id": 7,
      "tasks": ["7.3", "7.4", "9.4", "10.1", "10.2", "10.3", "10.4"]
    },
    {
      "id": 8,
      "tasks": ["10.5", "10.6", "11.1", "11.2", "11.3", "11.4"]
    },
    {
      "id": 9,
      "tasks": ["11.5", "11.6", "11.7", "12.1", "12.2"]
    },
    {
      "id": 10,
      "tasks": ["12.3", "13.1"]
    },
    {
      "id": 11,
      "tasks": ["13.2", "15.1"]
    },
    {
      "id": 12,
      "tasks": ["15.2", "15.3"]
    },
    {
      "id": 13,
      "tasks": ["16.1", "16.2", "16.3", "16.4"]
    },
    {
      "id": 14,
      "tasks": ["16.5", "17.1", "17.2", "17.3", "17.4", "17.5"]
    },
    {
      "id": 15,
      "tasks": ["17.6", "18.1", "18.2", "18.3"]
    },
    {
      "id": 16,
      "tasks": ["18.4", "19.1", "19.2"]
    },
    {
      "id": 17,
      "tasks": ["19.3", "21.1"]
    },
    {
      "id": 18,
      "tasks": ["21.2"]
    },
    {
      "id": 19,
      "tasks": ["21.3", "21.4", "21.5", "21.6"]
    },
    {
      "id": 20,
      "tasks": ["22.1", "22.2", "22.3", "22.4"]
    },
    {
      "id": 21,
      "tasks": ["23.1", "23.2", "23.3", "23.4", "23.5"]
    },
    {
      "id": 22,
      "tasks": ["24.1", "24.2", "24.3", "24.4"]
    },
    {
      "id": 23,
      "tasks": ["24.5"]
    },
    {
      "id": 24,
      "tasks": ["24.6", "25.1", "25.2", "25.3"]
    }
  ]
}
```
