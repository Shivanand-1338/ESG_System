/**
 * Navigation header component.
 * Requirements: 14.1
 */

import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const username = localStorage.getItem('username') || 'User';

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('username');
    localStorage.removeItem('tenant_id');
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname.startsWith(path);

  return (
    <header style={{ backgroundColor: '#1a237e', color: '#fff', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '56px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
        <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 700 }}>Breathe ESG</h2>
        <nav style={{ display: 'flex', gap: '16px' }}>
          <button
            onClick={() => navigate('/dashboard')}
            style={{
              background: 'none',
              border: 'none',
              color: isActive('/dashboard') ? '#fff' : '#b0bec5',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: isActive('/dashboard') ? 600 : 400,
              borderBottom: isActive('/dashboard') ? '2px solid #fff' : 'none',
              padding: '4px 0',
            }}
          >
            Dashboard
          </button>
        </nav>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <span style={{ fontSize: '14px', color: '#b0bec5' }}>{username}</span>
        <button
          onClick={handleLogout}
          style={{ padding: '6px 12px', backgroundColor: 'rgba(255,255,255,0.1)', color: '#fff', border: '1px solid rgba(255,255,255,0.3)', borderRadius: '4px', cursor: 'pointer', fontSize: '13px' }}
        >
          Logout
        </button>
      </div>
    </header>
  );
};

export default Header;
