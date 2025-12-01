/**
 * Componente de Rating con Estrellas
 * Sistema interactivo de 5 estrellas para valorar películas
 */

import React, { useState } from 'react';
import { StarRatingProps } from '../types';

const StarRating: React.FC<StarRatingProps> = ({
  rating,
  maxRating = 5,
  size = 24,
  onChange,
  readonly = false
}) => {
  const [hoverRating, setHoverRating] = useState<number>(0);

  const handleClick = (value: number) => {
    if (!readonly && onChange) {
      onChange(value);
    }
  };

  const handleMouseEnter = (value: number) => {
    if (!readonly) {
      setHoverRating(value);
    }
  };

  const handleMouseLeave = () => {
    if (!readonly) {
      setHoverRating(0);
    }
  };

  const displayRating = hoverRating || rating;

  return (
    <div 
      className="star-rating"
      style={{
        display: 'flex',
        gap: '2px',
        cursor: readonly ? 'default' : 'pointer'
      }}
    >
      {[...Array(maxRating)].map((_, index) => {
        const starValue = index + 1;
        const isFilled = starValue <= displayRating;
        const isHalf = starValue - 0.5 === displayRating;

        return (
          <div
            key={index}
            onClick={() => handleClick(starValue)}
            onMouseEnter={() => handleMouseEnter(starValue)}
            onMouseLeave={handleMouseLeave}
            style={{
              position: 'relative',
              width: `${size}px`,
              height: `${size}px`,
              transition: 'transform 0.2s'
            }}
            onMouseOver={(e) => {
              if (!readonly) {
                e.currentTarget.style.transform = 'scale(1.2)';
              }
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.transform = 'scale(1)';
            }}
          >
            {/* Estrella base (vacía) */}
            <svg
              width={size}
              height={size}
              viewBox="0 0 24 24"
              fill="none"
              stroke={isFilled || isHalf ? '#fbbf24' : '#d1d5db'}
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              style={{
                position: 'absolute',
                top: 0,
                left: 0
              }}
            >
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
            </svg>

            {/* Estrella rellena */}
            {(isFilled || isHalf) && (
              <svg
                width={size}
                height={size}
                viewBox="0 0 24 24"
                fill="#fbbf24"
                stroke="none"
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  clipPath: isHalf ? 'inset(0 50% 0 0)' : 'none'
                }}
              >
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
              </svg>
            )}
          </div>
        );
      })}
      
      {!readonly && hoverRating > 0 && (
        <span
          style={{
            marginLeft: '8px',
            fontSize: '14px',
            color: '#fbbf24',
            fontWeight: '600'
          }}
        >
          {hoverRating}/5
        </span>
      )}
    </div>
  );
};

export default StarRating;