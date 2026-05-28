/**
 * Raw data panel with JSON viewer.
 * Requirements: 6.5
 */

import React from 'react';

interface RawDataPanelProps {
  rawRecordId: string;
}

const RawDataPanel: React.FC<RawDataPanelProps> = ({ rawRecordId }) => {
  return (
    <div>
      <h4 style={{ color: '#333' }}>Raw Data</h4>
      <p style={{ color: '#666', fontSize: '14px' }}>Raw Record ID: {rawRecordId}</p>
      <div
        style={{
          backgroundColor: '#1e1e1e',
          color: '#d4d4d4',
          padding: '16px',
          borderRadius: '8px',
          fontFamily: 'monospace',
          fontSize: '13px',
          overflow: 'auto',
          maxHeight: '500px',
        }}
      >
        <pre style={{ margin: 0 }}>
          {JSON.stringify({ raw_record_id: rawRecordId, note: 'Full raw data available via API' }, null, 2)}
        </pre>
      </div>
    </div>
  );
};

export default RawDataPanel;
