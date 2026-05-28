/**
 * API service for approval workflow.
 * Requirements: 11.4, 11.5
 */

import api from './api';
import type { NormalizedRecord } from '../types';

export const approvalService = {
  async approveRecord(recordId: string, justification?: string, force?: boolean): Promise<NormalizedRecord> {
    const response = await api.post(`/v1/records/${recordId}/approve/`, {
      justification: justification || '',
      force: force || false,
    });
    return response.data;
  },

  async bulkApprove(recordIds: string[], justification?: string, force?: boolean): Promise<{
    approved_count: number;
    failed_count: number;
    approved: string[];
    failed: { id: string; reason: string }[];
  }> {
    const response = await api.post('/v1/records/bulk-approve/', {
      record_ids: recordIds,
      justification: justification || '',
      force: force || false,
    });
    return response.data;
  },

  async unapproveRecord(recordId: string, justification: string): Promise<NormalizedRecord> {
    const response = await api.post(`/v1/records/${recordId}/unapprove/`, {
      justification,
    });
    return response.data;
  },

  async dismissFlag(recordId: string, flagId: string, justification: string): Promise<NormalizedRecord> {
    const response = await api.post(`/v1/records/${recordId}/dismiss-flag/`, {
      flag_id: flagId,
      justification,
    });
    return response.data;
  },
};
