/**
 * Status badge component for displaying record/flag status.
 */

import React from 'react';

interface StatusBadgeProps {
  status: string;
  type?: 'approval' | 'scope' | 'flag';
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ status, type = 'approval' }) => {
  const getColor = () => {
    if (type === 'approval') {
      switch (status) {
        case 'APPROVED': return { bg: '#d4edda', color: '#155724' };
        case 'PENDING': return { bg: '#fff3cd', color: '#856404' };
        case 'FLAGGED': return { bg: '#f8d7da', color: '#721c24' };
        default: return { bg: '#e2e3e5', color: '#383d41' };
      }
    }
    if (type === 'scope') {
      switch (status) {
        case 'SCOPE_1': return { bg: '#cce5ff', color: '#004085' };
        case 'SCOPE_2': return { bg: '#d4edda', color: '#155724' };
        case 'SCOPE_3': return { bg: '#e2e3e5', color: '#383d41' };
        default: return { bg: '#e2e3e5', color: '#383d41' };
      }
    }
    if (type === 'flag') {
      switch (status) {
        case 'ACTIVE': return { bg: '#f8d7da', color: '#721c24' };
        case 'DISMISSED': return { bg: '#e2e3e5', color: '#383d41' };
        case 'RESOLVED': return { bg: '#d4edda', color: '#155724' };
        default: return { bg: '#e2e3e5', color: '#383d41' };
      }
    }
    return { bg: '#e2e3e5', color: '#383d41' };
  };

  const colors = getColor();

  return (
    <span
      style={{
        display: 'inline-block',
        padding: '2px 8px',
        borderRadius: '12px',
        fontSize: '12px',
        fontWeight: 600,
        backgroundColor: colors.bg,
        color: colors.color,
      }}
    >
      {status.replace('_', ' ')}
    </span>
  );
};

export default StatusBadge;
