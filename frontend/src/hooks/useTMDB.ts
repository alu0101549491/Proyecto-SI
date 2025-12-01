/**
 * Hook personalizado para interactuar con TMDB
 */

import { useState, useEffect } from 'react';
import { tmdbAPI } from '../api/tmdbAPI';
import { TMDBMovie, TMDBMovieDetails } from '../types';

/**
 * Hook para buscar una película en TMDB
 */
export const useTMDBSearch = (title: string) => {
  const [movie, setMovie] = useState<TMDBMovie | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!title) {
      setMovie(null);
      return;
    }

    const searchMovie = async () => {
      setLoading(true);
      setError(null);

      try {
        const result = await tmdbAPI.searchMovie(title);
        setMovie(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error desconocido');
      } finally {
        setLoading(false);
      }
    };

    // Debounce para evitar demasiadas búsquedas
    const timeoutId = setTimeout(searchMovie, 300);
    return () => clearTimeout(timeoutId);
  }, [title]);

  return { movie, loading, error };
};

/**
 * Hook para obtener detalles completos de una película
 */
export const useTMDBMovieDetails = (tmdbId: number | null) => {
  const [details, setDetails] = useState<TMDBMovieDetails | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!tmdbId) {
      setDetails(null);
      return;
    }

    const fetchDetails = async () => {
      setLoading(true);
      setError(null);

      try {
        const result = await tmdbAPI.getMovieDetails(tmdbId);
        setDetails(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error desconocido');
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [tmdbId]);

  return { details, loading, error };
};

/**
 * Hook para obtener películas similares
 */
export const useTMDBSimilar = (tmdbId: number | null, page: number = 1) => {
  const [movies, setMovies] = useState<TMDBMovie[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!tmdbId) {
      setMovies([]);
      return;
    }

    const fetchSimilar = async () => {
      setLoading(true);
      setError(null);

      try {
        const result = await tmdbAPI.getSimilarMovies(tmdbId, page);
        setMovies(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error desconocido');
      } finally {
        setLoading(false);
      }
    };

    fetchSimilar();
  }, [tmdbId, page]);

  return { movies, loading, error };
};

/**
 * Hook para obtener películas por género
 */
export const useTMDBByGenre = (genreId: number | null, page: number = 1) => {
  const [movies, setMovies] = useState<TMDBMovie[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!genreId) {
      setMovies([]);
      return;
    }

    const fetchByGenre = async () => {
      setLoading(true);
      setError(null);

      try {
        const result = await tmdbAPI.getMoviesByGenre(genreId, page);
        setMovies(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error desconocido');
      } finally {
        setLoading(false);
      }
    };

    fetchByGenre();
  }, [genreId, page]);

  return { movies, loading, error };
};