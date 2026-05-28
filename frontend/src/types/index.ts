/**
 * TypeScript type definitions for the Breathe ESG system.
 * Requirements: 6.1, 6.3, 6.6
 */

export interface ClientCompany {
  id: string;
  name: string;
  created_at: string;
  audit_lock_date: string | null;
}

export interface DataSource {
  id: string;
  client_company: string;
  client_company_name: string;
  source_type: 'SAP_IDOC' | 'SAP_CSV' | 'GREEN_BUTTON' | 'CONCUR_API';
  name: string;
  configuration: Record<string, unknown>;
  created_at: string;
}

export interface NormalizedRecord {
  id: string;
  client_company: string;
  client_company_name: string;
  raw_record: string;
  activity_date: string;
  emission_scope: 'SCOPE_1' | 'SCOPE_2' | 'SCOPE_3';
  emission_scope_display: string;
  activity_type: string;
  quantity: string;
  unit: string;
  location: string | null;
  original_quantity: string;
  original_unit: string;
  conversion_factor: string;
  approval_status: 'PENDING' | 'APPROVED' | 'FLAGGED';
  approval_status_display: string;
  approved_by: number | null;
  approved_by_username: string | null;
  approved_at: string | null;
  flags: SuspiciousFlag[];
  created_at: string;
  updated_at: string;
}

export interface NormalizedRecordListItem {
  id: string;
  client_company_name: string;
  activity_date: string;
  emission_scope: string;
  emission_scope_display: string;
  activity_type: string;
  quantity: string;
  unit: string;
  approval_status: string;
  approval_status_display: string;
  flag_count: number;
}

export interface SuspiciousFlag {
  id: string;
  record: string;
  flag_type: 'OUTLIER' | 'MISSING_FIELD' | 'INVALID_DATE' | 'CONVERSION_FAILURE' | 'DUPLICATE' | 'VALIDATION_RULE';
  description: string;
  status: 'ACTIVE' | 'DISMISSED' | 'RESOLVED';
  dismissed_by: number | null;
  dismissed_by_username: string | null;
  dismissed_at: string | null;
  dismissal_justification: string | null;
  created_at: string;
}

export interface AuditEvent {
  id: string;
  record: string;
  action_type: 'CREATE' | 'UPDATE' | 'APPROVE' | 'UNAPPROVE' | 'FLAG_CREATE' | 'FLAG_DISMISS';
  action_type_display: string;
  user: number | null;
  user_username: string | null;
  timestamp: string;
  field_name: string | null;
  old_value: string | null;
  new_value: string | null;
  justification: string | null;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface StatisticsSummary {
  total_records: number;
  approved_records: number;
  pending_records: number;
  flagged_records: number;
  suspicious_records: number;
  failed_records: number;
}

export interface StatisticsByScope {
  scope_1_count: number;
  scope_2_count: number;
  scope_3_count: number;
}

export interface RecordFilters {
  tenant_id?: string;
  source_type?: string;
  start_date?: string;
  end_date?: string;
  scope?: string;
  status?: string;
  page?: number;
  page_size?: number;
}
