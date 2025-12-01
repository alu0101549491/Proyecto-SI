/**
 * Componente de Tarjeta de Película
 * Muestra carátula con hover de rating
 */

import React, { useState } from 'react';
import { MovieCardProps } from '../types';
import StarRating from './StarRating';

const MovieCard: React.FC<MovieCardProps> = ({ movie, onRate, onClick }) => {
  const [isHovering, setIsHovering] = useState(false);
  const [tempRating, setTempRating] = useState(0);

  const handleRatingChange = (rating: number) => {
    setTempRating(rating);
  };

  const handleRatingConfirm = (rating: number) => {
    onRate(rating);
    setTempRating(0);
  };

  return (
    <div
      className="movie-card"
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => {
        setIsHovering(false);
        setTempRating(0);
      }}
      onClick={onClick}
      style={{
        position: 'relative',
        width: '200px',
        borderRadius: '12px',
        overflow: 'hidden',
        cursor: onClick ? 'pointer' : 'default',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        transition: 'transform 0.3s, box-shadow 0.3s',
        transform: isHovering ? 'translateY(-8px)' : 'translateY(0)',
        ...(isHovering && {
          boxShadow: '0 12px 24px rgba(0, 0, 0, 0.2)'
        })
      }}
    >
      {/* Carátula */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          paddingBottom: '150%', // Ratio 2:3
          backgroundColor: '#1f2937'
        }}
      >
        <img
          src={movie.poster_url || '/poster-placeholder.jpg'}
          alt={movie.title}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            transition: 'opacity 0.3s',
            opacity: isHovering ? 0.7 : 1
          }}
          onError={(e) => {
            e.currentTarget.src = '/poster-placeholder.jpg';
          }}
        />

        {/* Loading overlay */}
        {movie.is_loading && (
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
              color: 'white'
            }}
          >
            <div className="spinner">Cargando...</div>
          </div>
        )}

        {/* Overlay de rating al hacer hover */}
        {isHovering && !movie.is_loading && (
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              padding: '16px'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <p
              style={{
                color: 'white',
                fontSize: '14px',
                fontWeight: '600',
                marginBottom: '12px',
                textAlign: 'center'
              }}
            >
              Valora esta película
            </p>

            <StarRating
              rating={tempRating || movie.user_rating || 0}
              size={32}
              onChange={handleRatingChange}
            />

            {tempRating > 0 && (
              <button
                onClick={() => handleRatingConfirm(tempRating)}
                style={{
                  marginTop: '12px',
                  padding: '8px 16px',
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '12px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.backgroundColor = '#2563eb';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.backgroundColor = '#3b82f6';
                }}
              >
                Confirmar
              </button>
            )}

            {movie.user_rating && !tempRating && (
              <p
                style={{
                  marginTop: '8px',
                  color: '#9ca3af',
                  fontSize: '12px'
                }}
              >
                Tu valoración: {movie.user_rating}/5
              </p>
            )}
          </div>
        )}

        {/* Badge de ranking */}
        {movie.rank && (
          <div
            style={{
              position: 'absolute',
              top: '8px',
              left: '8px',
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              color: '#fbbf24',
              padding: '4px 8px',
              borderRadius: '6px',
              fontSize: '14px',
              fontWeight: '700'
            }}
          >
            #{movie.rank}
          </div>
        )}

        {/* Badge de rating predicho */}
        {movie.predicted_rating && !isHovering && (
          <div
            style={{
              position: 'absolute',
              top: '8px',
              right: '8px',
              backgroundColor: 'rgba(59, 130, 246, 0.9)',
              color: 'white',
              padding: '4px 8px',
              borderRadius: '6px',
              fontSize: '12px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            <span>⭐</span>
            <span>{movie.predicted_rating.toFixed(1)}</span>
          </div>
        )}
      </div>

      {/* Información de la película */}
      <div
        style={{
          padding: '12px',
          backgroundColor: '#1f2937',
          color: 'white'
        }}
      >
        <h3
          style={{
            margin: 0,
            fontSize: '14px',
            fontWeight: '600',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}
          title={movie.title}
        >
          {movie.title}
        </h3>

        {movie.release_date && (
          <p
            style={{
              margin: '4px 0 0 0',
              fontSize: '12px',
              color: '#9ca3af'
            }}
          >
            {new Date(movie.release_date).getFullYear()}
          </p>
        )}

        {movie.genres && movie.genres.length > 0 && (
          <div
            style={{
              marginTop: '8px',
              display: 'flex',
              flexWrap: 'wrap',
              gap: '4px'
            }}
          >
            {movie.genres.slice(0, 2).map((genre, index) => (
              <span
                key={index}
                style={{
                  fontSize: '10px',
                  padding: '2px 6px',
                  backgroundColor: '#374151',
                  borderRadius: '4px',
                  color: '#9ca3af'
                }}
              >
                {genre}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MovieCard;