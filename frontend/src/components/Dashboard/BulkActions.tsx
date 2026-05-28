/**
 * Bulk actions component for mass approval.
 * Requirements: 8.4
 */

import React, { useState } from 'react';
import { approvalService } from '../../services/approvalService';

interface BulkActionsProps {
  selectedIds: string[];
  onActionComplete: () => void;
}

const BulkActions: React.FC<BulkActionsProps> = ({ selectedIds, onActionComplete }) => {
  const [showModal, setShowModal] = useState(false);
  const [justification, setJustification] = useState('');
  const [force, setForce] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ approved_count: number; failed_count: number } | null>(null);

  const handleBulkApprove = async () => {
    setLoading(true);
    try {
      const res = await approvalService.bulkApprove(selectedIds, justification, force);
      setResult(res);
      onActionComplete();
    } catch (error) {
      console.error('Bulk approval failed:', error);
    } finally {
      setLoading(false);
    }
  };

  if (selectedIds.length === 0) return null;

  return (
    <>
      <div style={{ padding: '12px 16px', backgroundColor: '#e3f2fd', borderRadius: '8px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span style={{ fontWeight: 600 }}>{selectedIds.length} record(s) selected</span>
        <button
          onClick={() => setShowModal(true)}
          style={{ padding: '6px 16px', backgroundColor: '#28a745', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          Bulk Approve
        </button>
      </div>

      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ backgroundColor: '#fff', padding: '24px', borderRadius: '8px', maxWidth: '500px', width: '100%' }}>
            <h3 style={{ marginTop: 0 }}>Bulk Approve Records</h3>
            <p>You are about to approve {selectedIds.length} record(s).</p>
            
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', marginBottom: '4px', fontWeight: 600 }}>Justification (optional)</label>
              <textarea
                value={justification}
                onChange={(e) => setJustification(e.target.value)}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd', minHeight: '80px' }}
                placeholder="Enter justification for approval..."
              />
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input type="checkbox" checked={force} onChange={(e) => setForce(e.target.checked)} />
                Force approve (ignore unresolved flags)
              </label>
            </div>

            {result && (
              <div style={{ padding: '12px', backgroundColor: '#d4edda', borderRadius: '4px', marginBottom: '16px' }}>
                Approved: {result.approved_count} | Failed: {result.failed_count}
              </div>
            )}

            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
              <button
                onClick={() => { setShowModal(false); setResult(null); }}
                style={{ padding: '8px 16px', border: '1px solid #ddd', borderRadius: '4px', cursor: 'pointer' }}
              >
                Close
              </button>
              <button
                onClick={handleBulkApprove}
                disabled={loading}
                style={{ padding: '8px 16px', backgroundColor: '#28a745', color: '#fff', border: 'none', borderRadius: '4px', cursor: loading ? 'not-allowed' : 'pointer' }}
              >
                {loading ? 'Approving...' : 'Confirm Approval'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default BulkActions;
