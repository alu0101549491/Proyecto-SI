/**
 * Página de Detalle de Película
 * Muestra información completa y permite valorar
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTMDBMovieDetails, useTMDBSimilar } from '../hooks/useTMDB';
import { movieAPI } from '../api/movieAPI';
import StarRating from '../components/StarRating';
import MovieCard from '../components/MovieCard';

const MovieDetailPage: React.FC = () => {
  const { movieId } = useParams<{ movieId: string }>();
  const navigate = useNavigate();
  
  const [tmdbId, setTmdbId] = useState<number | null>(null);
  const [userRating, setUserRating] = useState<number>(0);
  const [predictedRating, setPredictedRating] = useState<number | null>(null);
  const [isRatingSubmitting, setIsRatingSubmitting] = useState(false);

  const { details, loading, error } = useTMDBMovieDetails(tmdbId);
  const { movies: similarMovies } = useTMDBSimilar(tmdbId, 1);

  // Cargar predicción de rating al montar
  useEffect(() => {
    if (movieId) {
      // Aquí deberías buscar el tmdbId desde tu backend
      // Por ahora, simulamos que lo tenemos
      setTmdbId(parseInt(movieId)); // Simplificación

      // Obtener predicción
      movieAPI.predictRating('user_demo', movieId)
        .then(rating => setPredictedRating(rating))
        .catch(err => console.error('Error prediciendo rating:', err));
    }
  }, [movieId]);

  const handleRatingSubmit = async (rating: number) => {
    if (!movieId) return;

    setIsRatingSubmitting(true);
    try {
      await movieAPI.addRating('user_demo', movieId, rating);
      setUserRating(rating);
      alert('✓ Rating guardado exitosamente');
    } catch (error) {
      console.error('Error guardando rating:', error);
      alert('Error al guardar el rating');
    } finally {
      setIsRatingSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div
        style={{
          minHeight: '100vh',
          backgroundColor: '#111827',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        <div style={{ textAlign: 'center' }}>
          <div
            style={{
              width: '48px',
              height: '48px',
              border: '4px solid #374151',
              borderTopColor: '#3b82f6',
              borderRadius: '50%',
              margin: '0 auto',
              animation: 'spin 1s linear infinite'
            }}
          />
          <p style={{ marginTop: '16px', color: '#9ca3af' }}>
            Cargando película...
          </p>
        </div>
      </div>
    );
  }

  if (error || !details) {
    return (
      <div
        style={{
          minHeight: '100vh',
          backgroundColor: '#111827',
          padding: '40px 20px',
          color: 'white'
        }}
      >
        <div style={{ maxWidth: '600px', margin: '0 auto', textAlign: 'center' }}>
          <h1 style={{ fontSize: '32px', marginBottom: '16px' }}>
            Película no encontrada
          </h1>
          <p style={{ color: '#9ca3af', marginBottom: '24px' }}>
            {error || 'No se pudo cargar la información de esta película'}
          </p>
          <button
            onClick={() => navigate('/')}
            style={{
              padding: '12px 24px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              cursor: 'pointer'
            }}
          >
            Volver al inicio
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: '#111827',
        color: 'white'
      }}
    >
      {/* Backdrop */}
      <div
        style={{
          position: 'relative',
          height: '500px',
          backgroundImage: details.backdrop_path
            ? `linear-gradient(to bottom, rgba(17, 24, 39, 0.3), rgba(17, 24, 39, 1)), url(https://image.tmdb.org/t/p/original${details.backdrop_path})`
            : 'none',
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        {/* Botón volver */}
        <button
          onClick={() => navigate('/')}
          style={{
            position: 'absolute',
            top: '20px',
            left: '20px',
            padding: '12px 20px',
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '14px',
            fontWeight: '600'
          }}
        >
          <span>←</span>
          Volver
        </button>
      </div>

      {/* Contenido principal */}
      <div
        style={{
          maxWidth: '1200px',
          margin: '-150px auto 0',
          padding: '0 24px 60px',
          position: 'relative'
        }}
      >
        <div style={{ display: 'flex', gap: '40px', flexWrap: 'wrap' }}>
          {/* Poster */}
          <img
            src={`https://image.tmdb.org/t/p/w500${details.poster_path}`}
            alt={details.title}
            style={{
              width: '300px',
              borderRadius: '12px',
              boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)'
            }}
          />

          {/* Información */}
          <div style={{ flex: 1, minWidth: '300px' }}>
            {/* Título */}
            <h1
              style={{
                fontSize: '48px',
                fontWeight: '700',
                marginBottom: '12px'
              }}
            >
              {details.title}
            </h1>

            {/* Tagline */}
            {details.tagline && (
              <p
                style={{
                  fontSize: '18px',
                  color: '#9ca3af',
                  fontStyle: 'italic',
                  marginBottom: '24px'
                }}
              >
                "{details.tagline}"
              </p>
            )}

            {/* Metadata */}
            <div
              style={{
                display: 'flex',
                gap: '20px',
                marginBottom: '24px',
                flexWrap: 'wrap'
              }}
            >
              <div>
                <span style={{ color: '#9ca3af' }}>Año: </span>
                <span>{new Date(details.release_date).getFullYear()}</span>
              </div>
              <div>
                <span style={{ color: '#9ca3af' }}>Duración: </span>
                <span>{details.runtime} min</span>
              </div>
              <div>
                <span style={{ color: '#9ca3af' }}>TMDB: </span>
                <span>⭐ {details.vote_average.toFixed(1)}/10</span>
              </div>
            </div>

            {/* Géneros */}
            <div style={{ marginBottom: '24px' }}>
              {details.genres.map(genre => (
                <span
                  key={genre.id}
                  style={{
                    display: 'inline-block',
                    padding: '6px 12px',
                    marginRight: '8px',
                    marginBottom: '8px',
                    backgroundColor: '#374151',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                >
                  {genre.name}
                </span>
              ))}
            </div>

            {/* Sistema de valoración */}
            <div
              style={{
                padding: '24px',
                backgroundColor: '#1f2937',
                borderRadius: '12px',
                marginBottom: '32px'
              }}
            >
              <h3 style={{ fontSize: '18px', marginBottom: '12px' }}>
                Tu Valoración
              </h3>
              
              {predictedRating && (
                <p style={{ color: '#9ca3af', fontSize: '14px', marginBottom: '12px' }}>
                  Creemos que te gustará: <strong>{predictedRating.toFixed(1)}/5 ⭐</strong>
                </p>
              )}

              <StarRating
                rating={userRating}
                size={40}
                onChange={handleRatingSubmit}
                readonly={isRatingSubmitting}
              />

              {isRatingSubmitting && (
                <p style={{ marginTop: '12px', color: '#3b82f6', fontSize: '14px' }}>
                  Guardando...
                </p>
              )}
            </div>

            {/* Sinopsis */}
            <h3 style={{ fontSize: '20px', marginBottom: '12px' }}>Sinopsis</h3>
            <p style={{ color: '#d1d5db', lineHeight: '1.6' }}>
              {details.overview || 'No hay sinopsis disponible.'}
            </p>
          </div>
        </div>

        {/* Películas similares */}
        {similarMovies.length > 0 && (
          <div style={{ marginTop: '60px' }}>
            <h2
              style={{
                fontSize: '28px',
                fontWeight: '700',
                marginBottom: '24px',
                borderLeft: '4px solid #3b82f6',
                paddingLeft: '16px'
              }}
            >
              Películas Similares
            </h2>
            <div
              style={{
                display: 'flex',
                gap: '20px',
                overflowX: 'auto',
                paddingBottom: '20px'
              }}
            >
              {similarMovies.slice(0, 10).map(movie => (
                <div key={movie.id} style={{ flexShrink: 0 }}>
                  <MovieCard
                    movie={{
                      movie_id: movie.id.toString(),
                      title: movie.title,
                      poster_url: `https://image.tmdb.org/t/p/w500${movie.poster_path}`,
                      release_date: movie.release_date,
                      vote_average: movie.vote_average
                    }}
                    onRate={(rating) => console.log('Rating:', rating)}
                    onClick={() => navigate(`/movie/${movie.id}`)}
                  />
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MovieDetailPage;