/**
 * API service for records operations.
 * Requirements: 11.2, 11.3, 11.6
 */

import api from './api';
import type { NormalizedRecord, NormalizedRecordListItem, PaginatedResponse, AuditEvent, RecordFilters } from '../types';

export const recordsService = {
  async getRecords(filters: RecordFilters = {}): Promise<PaginatedResponse<NormalizedRecordListItem>> {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        params.append(key, String(value));
      }
    });
    const response = await api.get(`/v1/records/?${params.toString()}`);
    return response.data;
  },

  async getRecord(id: string): Promise<NormalizedRecord> {
    const response = await api.get(`/v1/records/${id}/`);
    return response.data;
  },

  async getSuspiciousRecords(filters: RecordFilters = {}): Promise<PaginatedResponse<NormalizedRecord>> {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        params.append(key, String(value));
      }
    });
    const response = await api.get(`/v1/records/suspicious/?${params.toString()}`);
    return response.data;
  },

  async getAuditTrail(recordId: string): Promise<AuditEvent[]> {
    const response = await api.get(`/v1/records/${recordId}/audit-trail/`);
    return response.data;
  },
};
