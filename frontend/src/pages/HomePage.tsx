/**
 * Página Principal del Sistema de Recomendación
 * Muestra 3 secciones: Personalizadas, Top 10, Descubrimiento
 */

import React, { useState } from 'react';
import Header from '../components/Header';
import MovieSection from '../components/MovieSection';
import { useMovieRecommendations } from '../hooks/useMovieRecommendations';

const HomePage: React.FC = () => {
  // Usuario temporal (será reemplazado por el sistema de login)
  const [userId] = useState('user_demo');
  
  const {
    personalRecommendations,
    topMovies,
    discoveryMovies,
    loading,
    error,
    totalRatings,
    addRating,
    refresh
  } = useMovieRecommendations(userId);

  const [ratingLoading, setRatingLoading] = useState(false);

  const handleRate = async (movieId: string, rating: number) => {
    setRatingLoading(true);
    try {
      await addRating(movieId, rating);
      // Mostrar feedback visual (opcional)
      console.log(`✓ Rating guardado: película ${movieId} = ${rating} estrellas`);
    } catch (error) {
      console.error('Error al guardar rating:', error);
      alert('Error al guardar el rating. Por favor intenta de nuevo.');
    } finally {
      setRatingLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: '#111827',
        color: 'white'
      }}
    >
      {/* Contenedor principal */}
      <div
        style={{
          maxWidth: '1400px',
          margin: '0 auto',
          padding: '0 24px'
        }}
      >
        {/* Header */}
        <Header
          userName={userId.replace('user_', '').toUpperCase()}
          totalRatings={totalRatings}
          onRefresh={refresh}
        />

        {/* Loading inicial */}
        {loading && (
          <div
            style={{
              textAlign: 'center',
              padding: '60px 20px'
            }}
          >
            <div
              style={{
                display: 'inline-block',
                width: '48px',
                height: '48px',
                border: '4px solid #374151',
                borderTopColor: '#3b82f6',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }}
            />
            <p
              style={{
                marginTop: '16px',
                color: '#9ca3af',
                fontSize: '16px'
              }}
            >
              Cargando recomendaciones...
            </p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div
            style={{
              padding: '16px',
              backgroundColor: '#7f1d1d',
              border: '1px solid #991b1b',
              borderRadius: '8px',
              marginBottom: '24px'
            }}
          >
            <p style={{ margin: 0, color: '#fecaca' }}>
              ⚠️ Error: {error}
            </p>
          </div>
        )}

        {/* Overlay de carga al guardar rating */}
        {ratingLoading && (
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000
            }}
          >
            <div
              style={{
                backgroundColor: '#1f2937',
                padding: '24px 32px',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                gap: '16px'
              }}
            >
              <div
                style={{
                  width: '24px',
                  height: '24px',
                  border: '3px solid #374151',
                  borderTopColor: '#3b82f6',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }}
              />
              <span style={{ color: 'white', fontSize: '16px' }}>
                Guardando rating...
              </span>
            </div>
          </div>
        )}

        {/* Secciones de películas */}
        {!loading && (
          <>
            {/* 1. Sabemos que te gustará (Recomendaciones personalizadas) */}
            <MovieSection
              title="Sabemos que te gustará"
              movies={personalRecommendations}
              color="#ef4444" // Rojo
              onRate={handleRate}
            />

            {/* 2. En el Top 10 (Populares) */}
            <MovieSection
              title="En el Top 10"
              movies={topMovies}
              color="#8b5cf6" // Púrpura
              onRate={handleRate}
            />

            {/* 3. Podría Gustarte (Descubrimiento) */}
            <MovieSection
              title="Podría Gustarte"
              movies={discoveryMovies}
              color="#10b981" // Verde
              onRate={handleRate}
            />
          </>
        )}

        {/* Footer */}
        <footer
          style={{
            marginTop: '60px',
            paddingTop: '24px',
            paddingBottom: '24px',
            borderTop: '1px solid #374151',
            textAlign: 'center'
          }}
        >
          <p
            style={{
              color: '#6b7280',
              fontSize: '14px',
              margin: 0
            }}
          >
            Sistema de Recomendación de Películas - Grupo 8
          </p>
          <p
            style={{
              color: '#4b5563',
              fontSize: '12px',
              marginTop: '4px'
            }}
          >
            Fabián González Lence · Diego Hernández Chico · Miguel Martín Falagán
          </p>
        </footer>
      </div>

      {/* Estilos CSS en línea para animaciones */}
      <style>{`
        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }

        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }

        /* Scrollbar personalizado */
        .movie-section-scroll::-webkit-scrollbar {
          height: 8px;
        }

        .movie-section-scroll::-webkit-scrollbar-track {
          background: #1f2937;
          border-radius: 4px;
        }

        .movie-section-scroll::-webkit-scrollbar-thumb {
          background: #374151;
          border-radius: 4px;
        }

        .movie-section-scroll::-webkit-scrollbar-thumb:hover {
          background: #4b5563;
        }
      `}</style>
    </div>
  );
};

export default HomePage;