# Decisions Document

## Ambiguity Resolutions

### 1. SAP Data Format Selection
**Question:** SAP exports data in multiple formats (IDoc XML, CSV, BAPI, RFC). Which should we support?
**Decision:** Support both IDoc XML and CSV exports. IDoc is the standard for system-to-system integration, while CSV is common for manual exports and ad-hoc reporting.

### 2. Green Button Standard Version
**Question:** Green Button has multiple versions (DMD, CMD). Which to implement?
**Decision:** Implement Download My Data (DMD) file parsing. CMD requires OAuth2 integration with utility providers which adds complexity beyond the initial scope.

### 3. Emission Scope Classification Ambiguity
**Question:** How to handle activities that could belong to multiple scopes (e.g., on-site electricity generation)?
**Decision:** Use rule-based classification with a confidence flag. Ambiguous cases are flagged as `SuspiciousRecord` for analyst review. The analyst can override the scope with justification recorded in the audit trail.

### 4. Multi-Tenancy Isolation Level
**Question:** Separate databases, separate schemas, or shared schema?
**Decision:** Shared schema with row-level filtering. The expected tenant count (< 100) doesn't justify the operational complexity of separate databases. Permission classes enforce isolation at the API layer.

### 5. Anomaly Detection Threshold
**Question:** What z-score threshold should trigger a flag?
**Decision:** |z| > 3 (3 standard deviations), with a minimum of 30 historical records required before applying statistical detection. This balances sensitivity with false positive rate.

### 6. Approval Lock Behavior
**Question:** Should approved records be completely immutable or allow specific modifications?
**Decision:** Approved records lock core data fields (quantity, unit, scope, date). Metadata fields (location, notes) remain editable. Unapproval is possible before the audit lock date with justification.

### 7. Unit Conversion Ambiguity
**Question:** How to handle units that could have multiple interpretations (e.g., "gallons" could be US or UK)?
**Decision:** Default to US gallons unless the data source configuration specifies otherwise. Flag ambiguous conversions for analyst review.

### 8. Date Format Handling
**Question:** How to handle dates in various formats across sources?
**Decision:** Attempt parsing with multiple format patterns (ISO 8601, SAP YYYYMMDD, US MM/DD/YYYY, European DD/MM/YYYY). Fall back to current date if all parsing fails, with a flag created.

### 9. Duplicate Detection Strategy
**Question:** What constitutes a duplicate record?
**Decision:** Records with the same (data_source, activity_date, activity_type, quantity) tuple are flagged as potential duplicates. The second record is flagged, not rejected, allowing analyst judgment.

### 10. Authentication Mechanism
**Question:** JWT tokens, session auth, or token auth?
**Decision:** Django REST Framework TokenAuthentication for simplicity. Tokens don't expire (suitable for internal tools). Production deployment should add token rotation.
