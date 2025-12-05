/**
 * Hook personalizado para manejar recomendaciones de películas
 * Combina datos del backend con información de TMDB
 */

import { useState, useEffect, useCallback } from 'react';
import { movieAPI } from '../api/movieAPI';
import { tmdbAPI } from '../api/tmdbAPI';
import { EnrichedMovie } from '../types';

export const useMovieRecommendations = (userId: string) => {
  const [personalRecommendations, setPersonalRecommendations] = useState<EnrichedMovie[]>([]);
  const [topMovies, setTopMovies] = useState<EnrichedMovie[]>([]);
  const [discoveryMovies, setDiscoveryMovies] = useState<EnrichedMovie[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalRatings, setTotalRatings] = useState(0);

  /**
   * Enriquecer película con datos de TMDB
   */
  const enrichMovieWithTMDB = async (movie: {
    movie_id: string;
    title: string;
    predicted_rating?: number;
    average_rating?: number;
    rank?: number;
  }): Promise<EnrichedMovie> => {
    try {
      const tmdbMovie = await tmdbAPI.searchMovie(movie.title);
      
      if (tmdbMovie) {
        return {
          ...movie,
          tmdb_id: tmdbMovie.id,
          poster_url: tmdbAPI.getPosterUrl(tmdbMovie.poster_path, 'w500'),
          backdrop_url: tmdbAPI.getBackdropUrl(tmdbMovie.backdrop_path),
          overview: tmdbMovie.overview,
          release_date: tmdbMovie.release_date,
          vote_average: tmdbMovie.vote_average,
          genres: [], // Se podría mapear genre_ids a nombres
          is_loading: false
        };
      }
    } catch (error) {
      console.error(`Error enriqueciendo película ${movie.title}:`, error);
    }

    // Si no se encuentra en TMDB, devolver datos básicos
    return {
      ...movie,
      is_loading: false
    };
  };

  /**
   * Cargar recomendaciones personalizadas
   */
  const loadPersonalRecommendations = useCallback(async () => {
    try {
      const response = await movieAPI.getRecommendationsFromDB(userId, 20);
      
      // Enriquecer con TMDB en paralelo
      const enrichedPromises = response.recommendations.map(rec =>
        enrichMovieWithTMDB({
          movie_id: rec.movie_id,
          title: rec.title,
          predicted_rating: rec.predicted_rating,
          rank: rec.rank
        })
      );

      const enriched = await Promise.all(enrichedPromises);
      setPersonalRecommendations(enriched);
    } catch (error) {
      console.error('Error cargando recomendaciones personales:', error);
      // Si no hay ratings aún, es normal que falle
      setPersonalRecommendations([]);
    }
  }, [userId]);

  /**
   * Cargar top películas populares
   */
  const loadTopMovies = useCallback(async () => {
    try {
      const response = await movieAPI.getPopularMovies(10, 50);
      
      const enrichedPromises = response.map(movie =>
        enrichMovieWithTMDB({
          movie_id: movie.movie_id,
          title: movie.title,
          average_rating: movie.average_rating,
          rank: movie.rank
        })
      );

      const enriched = await Promise.all(enrichedPromises);
      setTopMovies(enriched);
    } catch (error) {
      console.error('Error cargando top películas:', error);
      setTopMovies([]);
    }
  }, []);

  /**
   * Cargar películas de descubrimiento (similares/relacionadas)
   * ACTUALIZADO: Excluye películas ya valoradas
   */
  const loadDiscoveryMovies = useCallback(async () => {
    try {
      // Obtener historial del usuario
      const history = await movieAPI.getUserHistory(userId);
      
      if (history.length === 0) {
        setDiscoveryMovies([]);
        return;
      }

      // Obtener películas similares a las mejor valoradas
      const topRated = history
        .filter(r => r.rating >= 4)
        .slice(0, 3);

      // CAMBIO CLAVE: Pasar userId para excluir películas ya valoradas
      const similarPromises = topRated.map(rating =>
        movieAPI.getSimilarMovies(rating.movie_id, 5, userId) // <-- AQUÍ
      );

      const similarResults = await Promise.all(similarPromises);
      const allSimilar = similarResults.flat();

      // Tomar las primeras 10 únicas
      const uniqueSimilar = Array.from(
        new Map(allSimilar.map(item => [item.movie_id, item])).values()
      ).slice(0, 10);

      const enrichedPromises = uniqueSimilar.map(movie =>
        enrichMovieWithTMDB({
          movie_id: movie.movie_id,
          title: movie.title,
          predicted_rating: movie.similarity_score
        })
      );

      const enriched = await Promise.all(enrichedPromises);
      setDiscoveryMovies(enriched);
    } catch (error) {
      console.error('Error cargando películas de descubrimiento:', error);
      setDiscoveryMovies([]);
    }
  }, [userId]);

  /**
   * Cargar todas las recomendaciones
   */
  const loadAll = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Cargar historial para saber cuántas películas ha valorado
      const history = await movieAPI.getUserHistory(userId);
      setTotalRatings(history.length);

      // Cargar las 3 secciones en paralelo
      await Promise.all([
        loadPersonalRecommendations(),
        loadTopMovies(),
        loadDiscoveryMovies()
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  }, [userId, loadPersonalRecommendations, loadTopMovies, loadDiscoveryMovies]);

  /**
   * Añadir rating y actualizar recomendaciones
   */
  const addRating = async (movieId: string, rating: number) => {
    try {
      await movieAPI.addRating(userId, movieId, rating);
      
      // Actualizar el rating local en todas las secciones
      const updateRating = (movies: EnrichedMovie[]) =>
        movies.map(m =>
          m.movie_id === movieId ? { ...m, user_rating: rating } : m
        );

      setPersonalRecommendations(prev => updateRating(prev));
      setTopMovies(prev => updateRating(prev));
      setDiscoveryMovies(prev => updateRating(prev));
      
      setTotalRatings(prev => prev + 1);

      // Recargar recomendaciones después de un breve delay
      setTimeout(() => {
        loadPersonalRecommendations();
      }, 500);
    } catch (error) {
      console.error('Error añadiendo rating:', error);
      throw error;
    }
  };

  // Cargar al montar el componente
  useEffect(() => {
    loadAll();
  }, [loadAll]);

  return {
    personalRecommendations,
    topMovies,
    discoveryMovies,
    loading,
    error,
    totalRatings,
    addRating,
    refresh: loadAll
  };
};