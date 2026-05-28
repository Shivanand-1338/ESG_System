/**
 * Normalized data panel showing all record fields.
 * Requirements: 6.5
 */

import React, { useState } from 'react';
import StatusBadge from '../Common/StatusBadge';
import { approvalService } from '../../services/approvalService';
import type { NormalizedRecord } from '../../types';

interface NormalizedDataPanelProps {
  record: NormalizedRecord;
  onRefresh: () => void;
}

const NormalizedDataPanel: React.FC<NormalizedDataPanelProps> = ({ record, onRefresh }) => {
  const [approving, setApproving] = useState(false);

  const handleApprove = async () => {
    setApproving(true);
    try {
      await approvalService.approveRecord(record.id);
      onRefresh();
    } catch (error) {
      console.error('Approval failed:', error);
      alert('Approval failed. Check for unresolved flags.');
    } finally {
      setApproving(false);
    }
  };

  const Field: React.FC<{ label: string; value: React.ReactNode }> = ({ label, value }) => (
    <div style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
      <div style={{ fontSize: '12px', color: '#666', fontWeight: 600 }}>{label}</div>
      <div style={{ fontSize: '14px', marginTop: '2px' }}>{value || '—'}</div>
    </div>
  );

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 32px' }}>
      <div>
        <h4 style={{ color: '#333', borderBottom: '2px solid #007bff', paddingBottom: '8px' }}>Activity Data</h4>
        <Field label="Activity Date" value={record.activity_date} />
        <Field label="Activity Type" value={record.activity_type} />
        <Field label="Emission Scope" value={<StatusBadge status={record.emission_scope} type="scope" />} />
        <Field label="Quantity" value={`${Number(record.quantity).toLocaleString()} ${record.unit}`} />
        <Field label="Location" value={record.location} />
      </div>

      <div>
        <h4 style={{ color: '#333', borderBottom: '2px solid #007bff', paddingBottom: '8px' }}>Source Attribution</h4>
        <Field label="Original Quantity" value={`${record.original_quantity} ${record.original_unit}`} />
        <Field label="Conversion Factor" value={record.conversion_factor} />
        <Field label="Client Company" value={record.client_company_name} />
        <Field label="Created At" value={new Date(record.created_at).toLocaleString()} />

        <h4 style={{ color: '#333', borderBottom: '2px solid #28a745', paddingBottom: '8px', marginTop: '24px' }}>Approval Status</h4>
        <Field label="Status" value={<StatusBadge status={record.approval_status} type="approval" />} />
        <Field label="Approved By" value={record.approved_by_username} />
        <Field label="Approved At" value={record.approved_at ? new Date(record.approved_at).toLocaleString() : null} />

        {record.approval_status === 'PENDING' && (
          <button
            onClick={handleApprove}
            disabled={approving}
            style={{ marginTop: '16px', padding: '8px 24px', backgroundColor: '#28a745', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
          >
            {approving ? 'Approving...' : 'Approve Record'}
          </button>
        )}
      </div>
    </div>
  );
};

export default NormalizedDataPanel;
