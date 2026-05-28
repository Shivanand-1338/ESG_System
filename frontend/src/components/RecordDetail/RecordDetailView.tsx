/**
 * Record detail view with tabbed interface.
 * Requirements: 6.5
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { recordsService } from '../../services/recordsService';
import NormalizedDataPanel from './NormalizedDataPanel';
import RawDataPanel from './RawDataPanel';
import AuditTrailPanel from './AuditTrailPanel';
import FlagsPanel from './FlagsPanel';
import type { NormalizedRecord } from '../../types';

const RecordDetailView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [record, setRecord] = useState<NormalizedRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'normalized' | 'raw' | 'audit' | 'flags'>('normalized');

  useEffect(() => {
    if (id) loadRecord(id);
  }, [id]);

  const loadRecord = async (recordId: string) => {
    try {
      const data = await recordsService.getRecord(recordId);
      setRecord(data);
    } catch (error) {
      console.error('Failed to load record:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div style={{ padding: '24px' }}>Loading record...</div>;
  if (!record) return <div style={{ padding: '24px' }}>Record not found</div>;

  const tabs = [
    { key: 'normalized', label: 'Normalized Data' },
    { key: 'raw', label: 'Raw Data' },
    { key: 'audit', label: 'Audit Trail' },
    { key: 'flags', label: `Flags (${record.flags?.length || 0})` },
  ] as const;

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
        <button onClick={() => navigate('/dashboard')} style={{ padding: '6px 12px', cursor: 'pointer' }}>
          ← Back
        </button>
        <h2 style={{ margin: 0 }}>Record Detail</h2>
        <span style={{ color: '#666', fontSize: '14px' }}>{record.id}</span>
      </div>

      <div style={{ display: 'flex', gap: '0', borderBottom: '2px solid #dee2e6', marginBottom: '16px' }}>
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            style={{
              padding: '10px 20px',
              border: 'none',
              borderBottom: activeTab === tab.key ? '3px solid #007bff' : '3px solid transparent',
              backgroundColor: 'transparent',
              cursor: 'pointer',
              fontWeight: activeTab === tab.key ? 600 : 400,
              color: activeTab === tab.key ? '#007bff' : '#666',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'normalized' && <NormalizedDataPanel record={record} onRefresh={() => id && loadRecord(id)} />}
      {activeTab === 'raw' && <RawDataPanel rawRecordId={record.raw_record} />}
      {activeTab === 'audit' && <AuditTrailPanel recordId={record.id} />}
      {activeTab === 'flags' && <FlagsPanel record={record} onRefresh={() => id && loadRecord(id)} />}
    </div>
  );
};

export default RecordDetailView;
