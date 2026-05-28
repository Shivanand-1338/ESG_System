/**
 * Suspicious flags panel with dismiss action.
 * Requirements: 6.3, 7.6
 */

import React, { useState } from 'react';
import StatusBadge from '../Common/StatusBadge';
import { approvalService } from '../../services/approvalService';
import type { NormalizedRecord, SuspiciousFlag } from '../../types';

interface FlagsPanelProps {
  record: NormalizedRecord;
  onRefresh: () => void;
}

const FlagsPanel: React.FC<FlagsPanelProps> = ({ record, onRefresh }) => {
  const [dismissingId, setDismissingId] = useState<string | null>(null);
  const [justification, setJustification] = useState('');

  const handleDismiss = async (flag: SuspiciousFlag) => {
    if (!justification.trim()) {
      alert('Justification is required to dismiss a flag.');
      return;
    }

    try {
      await approvalService.dismissFlag(record.id, flag.id, justification);
      setDismissingId(null);
      setJustification('');
      onRefresh();
    } catch (error) {
      console.error('Failed to dismiss flag:', error);
    }
  };

  const flags = record.flags || [];

  return (
    <div>
      <h4 style={{ color: '#333' }}>Suspicious Flags ({flags.length})</h4>

      {flags.length === 0 ? (
        <p style={{ color: '#666' }}>No flags on this record.</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {flags.map((flag) => (
            <div
              key={flag.id}
              style={{
                padding: '16px',
                borderRadius: '8px',
                border: `1px solid ${flag.status === 'ACTIVE' ? '#f5c6cb' : '#d6d8db'}`,
                backgroundColor: flag.status === 'ACTIVE' ? '#fff5f5' : '#f8f9fa',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <span style={{ fontWeight: 600 }}>{flag.flag_type.replace('_', ' ')}</span>
                  <StatusBadge status={flag.status} type="flag" />
                </div>
                <span style={{ fontSize: '12px', color: '#666' }}>
                  {new Date(flag.created_at).toLocaleString()}
                </span>
              </div>

              <p style={{ margin: '8px 0', fontSize: '14px', color: '#555' }}>{flag.description}</p>

              {flag.status === 'DISMISSED' && (
                <div style={{ fontSize: '13px', color: '#666' }}>
                  Dismissed by {flag.dismissed_by_username} on {flag.dismissed_at ? new Date(flag.dismissed_at).toLocaleString() : ''}
                  {flag.dismissal_justification && <div style={{ fontStyle: 'italic' }}>"{flag.dismissal_justification}"</div>}
                </div>
              )}

              {flag.status === 'ACTIVE' && (
                <>
                  {dismissingId === flag.id ? (
                    <div style={{ marginTop: '8px' }}>
                      <textarea
                        value={justification}
                        onChange={(e) => setJustification(e.target.value)}
                        placeholder="Enter justification for dismissal..."
                        style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd', minHeight: '60px' }}
                      />
                      <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                        <button
                          onClick={() => handleDismiss(flag)}
                          style={{ padding: '6px 12px', backgroundColor: '#6c757d', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                        >
                          Confirm Dismiss
                        </button>
                        <button
                          onClick={() => { setDismissingId(null); setJustification(''); }}
                          style={{ padding: '6px 12px', border: '1px solid #ddd', borderRadius: '4px', cursor: 'pointer' }}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => setDismissingId(flag.id)}
                      style={{ marginTop: '8px', padding: '6px 12px', border: '1px solid #6c757d', borderRadius: '4px', cursor: 'pointer', backgroundColor: '#fff' }}
                    >
                      Dismiss Flag
                    </button>
                  )}
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FlagsPanel;
