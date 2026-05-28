/**
 * Audit trail timeline panel.
 * Requirements: 6.6
 */

import React, { useEffect, useState } from 'react';
import { recordsService } from '../../services/recordsService';
import type { AuditEvent } from '../../types';

interface AuditTrailPanelProps {
  recordId: string;
}

const AuditTrailPanel: React.FC<AuditTrailPanelProps> = ({ recordId }) => {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAuditTrail();
  }, [recordId]);

  const loadAuditTrail = async () => {
    try {
      const data = await recordsService.getAuditTrail(recordId);
      setEvents(data);
    } catch (error) {
      console.error('Failed to load audit trail:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading audit trail...</div>;

  const getActionColor = (actionType: string) => {
    switch (actionType) {
      case 'CREATE': return '#007bff';
      case 'UPDATE': return '#ffc107';
      case 'APPROVE': return '#28a745';
      case 'UNAPPROVE': return '#dc3545';
      case 'FLAG_CREATE': return '#dc3545';
      case 'FLAG_DISMISS': return '#6c757d';
      default: return '#333';
    }
  };

  return (
    <div>
      <h4 style={{ color: '#333' }}>Audit Trail ({events.length} events)</h4>
      
      {events.length === 0 ? (
        <p style={{ color: '#666' }}>No audit events found.</p>
      ) : (
        <div style={{ position: 'relative', paddingLeft: '24px' }}>
          <div style={{ position: 'absolute', left: '8px', top: 0, bottom: 0, width: '2px', backgroundColor: '#dee2e6' }} />
          
          {events.map((event) => (
            <div key={event.id} style={{ position: 'relative', marginBottom: '16px', paddingLeft: '16px' }}>
              <div
                style={{
                  position: 'absolute',
                  left: '-20px',
                  top: '4px',
                  width: '12px',
                  height: '12px',
                  borderRadius: '50%',
                  backgroundColor: getActionColor(event.action_type),
                }}
              />
              
              <div style={{ backgroundColor: '#f8f9fa', padding: '12px', borderRadius: '6px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 600, color: getActionColor(event.action_type) }}>
                    {event.action_type_display}
                  </span>
                  <span style={{ fontSize: '12px', color: '#666' }}>
                    {new Date(event.timestamp).toLocaleString()}
                  </span>
                </div>
                
                {event.user_username && (
                  <div style={{ fontSize: '13px', color: '#666', marginTop: '4px' }}>
                    By: {event.user_username}
                  </div>
                )}
                
                {event.field_name && (
                  <div style={{ fontSize: '13px', marginTop: '4px' }}>
                    <strong>{event.field_name}:</strong> {event.old_value || '(empty)'} → {event.new_value || '(empty)'}
                  </div>
                )}
                
                {event.justification && (
                  <div style={{ fontSize: '13px', color: '#555', marginTop: '4px', fontStyle: 'italic' }}>
                    "{event.justification}"
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AuditTrailPanel;
