/**
 * Componente Header
 * Cabecera con saludo personalizado y estadísticas
 */

import React from 'react';

interface HeaderProps {
  userName: string;
  totalRatings?: number;
  onRefresh?: () => void;
}

const Header: React.FC<HeaderProps> = ({ userName, totalRatings = 0, onRefresh }) => {
  return (
    <header
      style={{
        marginBottom: '48px',
        padding: '32px 0',
        borderBottom: '1px solid #374151'
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px'
        }}
      >
        {/* Saludo */}
        <div>
          <h1
            style={{
              fontSize: '36px',
              fontWeight: '700',
              color: 'white',
              margin: 0,
              marginBottom: '8px'
            }}
          >
            Hola, <span style={{ color: '#3b82f6' }}>{userName}</span>
          </h1>
          <p
            style={{
              fontSize: '16px',
              color: '#9ca3af',
              margin: 0
            }}
          >
            {totalRatings > 0
              ? `Has valorado ${totalRatings} película${totalRatings !== 1 ? 's' : ''}`
              : 'Empieza a valorar películas para obtener recomendaciones personalizadas'}
          </p>
        </div>

        {/* Botón de refrescar */}
        {onRefresh && (
          <button
            onClick={onRefresh}
            style={{
              padding: '12px 24px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'background-color 0.2s, transform 0.2s'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = '#2563eb';
              e.currentTarget.style.transform = 'scale(1.05)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = '#3b82f6';
              e.currentTarget.style.transform = 'scale(1)';
            }}
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="23 4 23 10 17 10"></polyline>
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
            </svg>
            Actualizar Recomendaciones
          </button>
        )}
      </div>
    </header>
  );
};

export default Header;