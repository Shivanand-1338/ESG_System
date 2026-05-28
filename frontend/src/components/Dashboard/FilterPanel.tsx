/**
 * Filter panel component for records.
 * Requirements: 6.4
 */

import React from 'react';
import type { RecordFilters } from '../../types';

interface FilterPanelProps {
  filters: RecordFilters;
  onFilterChange: (filters: RecordFilters) => void;
}

const FilterPanel: React.FC<FilterPanelProps> = ({ filters, onFilterChange }) => {
  const handleChange = (key: keyof RecordFilters, value: string) => {
    onFilterChange({ ...filters, [key]: value || undefined, page: 1 });
  };

  return (
    <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', padding: '16px', backgroundColor: '#f8f9fa', borderRadius: '8px', marginBottom: '16px' }}>
      <div>
        <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, marginBottom: '4px' }}>Source Type</label>
        <select
          value={filters.source_type || ''}
          onChange={(e) => handleChange('source_type', e.target.value)}
          style={{ padding: '6px 12px', borderRadius: '4px', border: '1px solid #ddd' }}
        >
          <option value="">All Sources</option>
          <option value="SAP_IDOC">SAP IDoc</option>
          <option value="SAP_CSV">SAP CSV</option>
          <option value="GREEN_BUTTON">Green Button</option>
          <option value="CONCUR_API">Concur</option>
        </select>
      </div>

      <div>
        <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, marginBottom: '4px' }}>Emission Scope</label>
        <select
          value={filters.scope || ''}
          onChange={(e) => handleChange('scope', e.target.value)}
          style={{ padding: '6px 12px', borderRadius: '4px', border: '1px solid #ddd' }}
        >
          <option value="">All Scopes</option>
          <option value="SCOPE_1">Scope 1</option>
          <option value="SCOPE_2">Scope 2</option>
          <option value="SCOPE_3">Scope 3</option>
        </select>
      </div>

      <div>
        <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, marginBottom: '4px' }}>Status</label>
        <select
          value={filters.status || ''}
          onChange={(e) => handleChange('status', e.target.value)}
          style={{ padding: '6px 12px', borderRadius: '4px', border: '1px solid #ddd' }}
        >
          <option value="">All Statuses</option>
          <option value="PENDING">Pending</option>
          <option value="APPROVED">Approved</option>
          <option value="FLAGGED">Flagged</option>
        </select>
      </div>

      <div>
        <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, marginBottom: '4px' }}>Start Date</label>
        <input
          type="date"
          value={filters.start_date || ''}
          onChange={(e) => handleChange('start_date', e.target.value)}
          style={{ padding: '6px 12px', borderRadius: '4px', border: '1px solid #ddd' }}
        />
      </div>

      <div>
        <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, marginBottom: '4px' }}>End Date</label>
        <input
          type="date"
          value={filters.end_date || ''}
          onChange={(e) => handleChange('end_date', e.target.value)}
          style={{ padding: '6px 12px', borderRadius: '4px', border: '1px solid #ddd' }}
        />
      </div>

      <div style={{ display: 'flex', alignItems: 'flex-end' }}>
        <button
          onClick={() => onFilterChange({ page: 1 })}
          style={{ padding: '6px 16px', borderRadius: '4px', border: '1px solid #ddd', cursor: 'pointer', backgroundColor: '#fff' }}
        >
          Clear Filters
        </button>
      </div>
    </div>
  );
};

export default FilterPanel;
