/**
 * Record table component with sorting and filtering.
 * Requirements: 6.1
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import StatusBadge from '../Common/StatusBadge';
import type { NormalizedRecordListItem } from '../../types';

interface RecordTableProps {
  records: NormalizedRecordListItem[];
  selectedIds: string[];
  onSelectionChange: (ids: string[]) => void;
}

const RecordTable: React.FC<RecordTableProps> = ({ records, selectedIds, onSelectionChange }) => {
  const navigate = useNavigate();
  const [sortField, setSortField] = useState<string>('activity_date');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDir('asc');
    }
  };

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      onSelectionChange(records.map((r) => r.id));
    } else {
      onSelectionChange([]);
    }
  };

  const handleSelectRow = (id: string, checked: boolean) => {
    if (checked) {
      onSelectionChange([...selectedIds, id]);
    } else {
      onSelectionChange(selectedIds.filter((i) => i !== id));
    }
  };

  const sortedRecords = [...records].sort((a, b) => {
    const aVal = (a as unknown as Record<string, unknown>)[sortField] as string;
    const bVal = (b as unknown as Record<string, unknown>)[sortField] as string;
    const cmp = String(aVal || '').localeCompare(String(bVal || ''));
    return sortDir === 'asc' ? cmp : -cmp;
  });

  const SortHeader: React.FC<{ field: string; label: string }> = ({ field, label }) => (
    <th
      onClick={() => handleSort(field)}
      style={{ cursor: 'pointer', padding: '10px 12px', textAlign: 'left', borderBottom: '2px solid #dee2e6', userSelect: 'none' }}
    >
      {label} {sortField === field ? (sortDir === 'asc' ? '▲' : '▼') : ''}
    </th>
  );

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: '#fff' }}>
        <thead>
          <tr style={{ backgroundColor: '#f8f9fa' }}>
            <th style={{ padding: '10px 12px', borderBottom: '2px solid #dee2e6' }}>
              <input
                type="checkbox"
                checked={selectedIds.length === records.length && records.length > 0}
                onChange={(e) => handleSelectAll(e.target.checked)}
              />
            </th>
            <SortHeader field="activity_date" label="Date" />
            <SortHeader field="activity_type" label="Activity Type" />
            <SortHeader field="emission_scope" label="Scope" />
            <SortHeader field="quantity" label="Quantity" />
            <th style={{ padding: '10px 12px', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>Unit</th>
            <SortHeader field="approval_status" label="Status" />
            <th style={{ padding: '10px 12px', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>Flags</th>
          </tr>
        </thead>
        <tbody>
          {sortedRecords.length === 0 ? (
            <tr>
              <td colSpan={8} style={{ padding: '24px', textAlign: 'center', color: '#666' }}>
                No records found
              </td>
            </tr>
          ) : (
            sortedRecords.map((record) => (
              <tr
                key={record.id}
                onClick={() => navigate(`/records/${record.id}`)}
                style={{ cursor: 'pointer', borderBottom: '1px solid #dee2e6' }}
                onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#f8f9fa')}
                onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '')}
              >
                <td style={{ padding: '10px 12px' }} onClick={(e) => e.stopPropagation()}>
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(record.id)}
                    onChange={(e) => handleSelectRow(record.id, e.target.checked)}
                  />
                </td>
                <td style={{ padding: '10px 12px' }}>{record.activity_date}</td>
                <td style={{ padding: '10px 12px' }}>{record.activity_type}</td>
                <td style={{ padding: '10px 12px' }}>
                  <StatusBadge status={record.emission_scope} type="scope" />
                </td>
                <td style={{ padding: '10px 12px' }}>{Number(record.quantity).toLocaleString()}</td>
                <td style={{ padding: '10px 12px' }}>{record.unit}</td>
                <td style={{ padding: '10px 12px' }}>
                  <StatusBadge status={record.approval_status} type="approval" />
                </td>
                <td style={{ padding: '10px 12px' }}>
                  {record.flag_count > 0 && (
                    <span style={{ color: '#dc3545', fontWeight: 'bold' }}>⚠ {record.flag_count}</span>
                  )}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default RecordTable;
