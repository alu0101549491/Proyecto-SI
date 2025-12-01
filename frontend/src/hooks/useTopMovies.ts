/**
 * Hook personalizado para obtener películas más populares
 */

import { useState, useEffect, useCallback } from 'react';
import { movieAPI } from '../api/movieAPI';
import { EnrichedMovie } from '../types';

export const useTopMovies = (n: number = 10, minRatings: number = 50) => {
  const [movies, setMovies] = useState<EnrichedMovie[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTopMovies = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await movieAPI.getPopularMovies(n, minRatings);
      
      // Convertir a EnrichedMovie (sin TMDB por ahora)
      const enriched: EnrichedMovie[] = result.map(movie => ({
        movie_id: movie.movie_id,
        title: `Movie ${movie.movie_id}`, // Título temporal
        average_rating: movie.average_rating,
        rank: movie.rank,
        is_loading: false
      }));

      setMovies(enriched);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
      setMovies([]);
    } finally {
      setLoading(false);
    }
  }, [n, minRatings]);

  useEffect(() => {
    fetchTopMovies();
  }, [fetchTopMovies]);

  return {
    movies,
    loading,
    error,
    refetch: fetchTopMovies
  };
};