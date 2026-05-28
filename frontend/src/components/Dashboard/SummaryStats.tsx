/**
 * Summary statistics cards component.
 * Requirements: 6.7
 */

import React, { useEffect, useState } from 'react';
import { statisticsService } from '../../services/statisticsService';
import type { StatisticsSummary } from '../../types';

const SummaryStats: React.FC = () => {
  const [stats, setStats] = useState<StatisticsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await statisticsService.getSummary();
      setStats(data);
    } catch (error) {
      console.error('Failed to load statistics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading statistics...</div>;
  if (!stats) return <div>Failed to load statistics</div>;

  const cards = [
    { label: 'Total Records', value: stats.total_records, color: '#007bff' },
    { label: 'Approved', value: stats.approved_records, color: '#28a745' },
    { label: 'Pending', value: stats.pending_records, color: '#ffc107' },
    { label: 'Suspicious', value: stats.suspicious_records, color: '#dc3545' },
    { label: 'Failed', value: stats.failed_records, color: '#6c757d' },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px', marginBottom: '24px' }}>
      {cards.map((card) => (
        <div
          key={card.label}
          style={{
            padding: '16px',
            borderRadius: '8px',
            backgroundColor: '#fff',
            border: `2px solid ${card.color}`,
            textAlign: 'center',
          }}
        >
          <div style={{ fontSize: '28px', fontWeight: 'bold', color: card.color }}>
            {card.value}
          </div>
          <div style={{ fontSize: '14px', color: '#666', marginTop: '4px' }}>
            {card.label}
          </div>
        </div>
      ))}
    </div>
  );
};

export default SummaryStats;
