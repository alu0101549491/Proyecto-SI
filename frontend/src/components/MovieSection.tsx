/**
 * Componente de Sección de Películas
 * Muestra una lista horizontal de películas con scroll
 */

import React from 'react';
import { MovieSectionProps } from '../types';
import MovieCard from './MovieCard';

const MovieSection: React.FC<MovieSectionProps> = ({
  title,
  movies,
  color = '#3b82f6',
  onRate,
  loading = false
}) => {
  return (
    <section
      style={{
        marginBottom: '48px'
      }}
    >
      {/* Título de la sección */}
      <h2
        style={{
          fontSize: '24px',
          fontWeight: '700',
          marginBottom: '20px',
          color: 'white',
          borderLeft: `4px solid ${color}`,
          paddingLeft: '16px'
        }}
      >
        {title}
      </h2>

      {/* Loading state */}
      {loading ? (
        <div
          style={{
            display: 'flex',
            gap: '16px',
            overflowX: 'auto',
            paddingBottom: '16px'
          }}
        >
          {[...Array(6)].map((_, index) => (
            <div
              key={index}
              style={{
                width: '200px',
                height: '300px',
                backgroundColor: '#374151',
                borderRadius: '12px',
                animation: 'pulse 2s infinite',
                flexShrink: 0
              }}
            />
          ))}
        </div>
      ) : movies.length === 0 ? (
        // Empty state
        <div
          style={{
            padding: '48px',
            textAlign: 'center',
            backgroundColor: '#1f2937',
            borderRadius: '12px',
            border: '2px dashed #374151'
          }}
        >
          <p
            style={{
              color: '#9ca3af',
              fontSize: '16px',
              margin: 0
            }}
          >
            No hay películas para mostrar
          </p>
          <p
            style={{
              color: '#6b7280',
              fontSize: '14px',
              marginTop: '8px'
            }}
          >
            Valora algunas películas para obtener recomendaciones personalizadas
          </p>
        </div>
      ) : (
        // Movies grid/carousel
        <div
          style={{
            display: 'flex',
            gap: '20px',
            overflowX: 'auto',
            paddingBottom: '16px',
            scrollbarWidth: 'thin',
            scrollbarColor: `${color} #1f2937`
          }}
          className="movie-section-scroll"
        >
          {movies.map((movie) => (
            <div
              key={movie.movie_id}
              style={{
                flexShrink: 0
              }}
            >
              <MovieCard
                movie={movie}
                onRate={(rating) => onRate(movie.movie_id, rating)}
              />
            </div>
          ))}
        </div>
      )}
    </section>
  );
};

export default MovieSection;