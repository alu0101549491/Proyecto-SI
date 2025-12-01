/**
 * Cliente API para The Movie Database (TMDB)
 * Documentación: https://developers.themoviedb.org/3
 */

import axios, { AxiosInstance } from 'axios';
import { TMDBMovie, TMDBMovieDetails, TMDBSearchResponse } from '../types';

const TMDB_BASE_URL = 'https://api.themoviedb.org/3';
const TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p';

class TMDBAPIClient {
  private client: AxiosInstance;
  private apiKey: string;

  constructor() {
    this.apiKey = import.meta.env.VITE_TMDB_API_KEY || '';
    
    if (!this.apiKey) {
      console.warn('⚠️ TMDB API Key no configurada. Las carátulas no funcionarán.');
    }

    this.client = axios.create({
      baseURL: TMDB_BASE_URL,
      params: {
        api_key: this.apiKey,
        language: 'es-ES' // Español
      }
    });
  }

  /**
   * Buscar película por título
   */
  async searchMovie(title: string): Promise<TMDBMovie | null> {
    try {
      // Limpiar título (quitar año entre paréntesis)
      const cleanTitle = title.replace(/\s*\(\d{4}\)\s*$/, '').trim();
      
      const response = await this.client.get<TMDBSearchResponse>('/search/movie', {
        params: {
          query: cleanTitle,
          include_adult: false
        }
      });

      if (response.data.results.length > 0) {
        return response.data.results[0]; // Devolver primer resultado
      }

      return null;
    } catch (error) {
      console.error(`Error buscando película "${title}":`, error);
      return null;
    }
  }

  /**
   * Obtener detalles completos de una película por ID de TMDB
   */
  async getMovieDetails(tmdbId: number): Promise<TMDBMovieDetails | null> {
    try {
      const response = await this.client.get<TMDBMovieDetails>(`/movie/${tmdbId}`);
      return response.data;
    } catch (error) {
      console.error(`Error obteniendo detalles de película ${tmdbId}:`, error);
      return null;
    }
  }

  /**
   * Obtener URL de poster (carátula)
   */
  getPosterUrl(posterPath: string | null, size: 'w200' | 'w500' | 'original' = 'w500'): string {
    if (!posterPath) {
      return 'https://via.placeholder.com/500x750?text=Snpm i --save-dev @types/nodein+Carátula';
    }
    return `${TMDB_IMAGE_BASE_URL}/${size}${posterPath}`;
  }

  /**
   * Obtener URL de backdrop (imagen de fondo)
   */
  getBackdropUrl(backdropPath: string | null, size: 'w780' | 'w1280' | 'original' = 'w1280'): string {
    if (!backdropPath) {
      return 'https://via.placeholder.com/1280x720?text=Sin+Imagen';
    }
    return `${TMDB_IMAGE_BASE_URL}/${size}${backdropPath}`;
  }

  /**
   * Buscar múltiples películas en batch
   * Optimizado para evitar rate limits
   */
  async searchMoviesBatch(titles: string[]): Promise<Map<string, TMDBMovie>> {
    const results = new Map<string, TMDBMovie>();
    
    // Limitar a 40 requests/10 segundos (rate limit de TMDB)
    const batchSize = 5;
    const delay = 250; // 250ms entre requests

    for (let i = 0; i < titles.length; i += batchSize) {
      const batch = titles.slice(i, i + batchSize);
      
      const promises = batch.map(async (title) => {
        const movie = await this.searchMovie(title);
        if (movie) {
          results.set(title, movie);
        }
      });

      await Promise.all(promises);
      
      // Esperar entre batches
      if (i + batchSize < titles.length) {
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    return results;
  }

  /**
   * Obtener películas recomendadas basadas en una película
   */
  async getRecommendations(tmdbId: number, page: number = 1): Promise<TMDBMovie[]> {
    try {
      const response = await this.client.get<TMDBSearchResponse>(
        `/movie/${tmdbId}/recommendations`,
        { params: { page } }
      );
      return response.data.results;
    } catch (error) {
      console.error(`Error obteniendo recomendaciones para ${tmdbId}:`, error);
      return [];
    }
  }

  /**
   * Obtener películas similares
   */
  async getSimilarMovies(tmdbId: number, page: number = 1): Promise<TMDBMovie[]> {
    try {
      const response = await this.client.get<TMDBSearchResponse>(
        `/movie/${tmdbId}/similar`,
        { params: { page } }
      );
      return response.data.results;
    } catch (error) {
      console.error(`Error obteniendo similares para ${tmdbId}:`, error);
      return [];
    }
  }

  /**
   * Obtener películas por género
   */
  async getMoviesByGenre(genreId: number, page: number = 1): Promise<TMDBMovie[]> {
    try {
      const response = await this.client.get<TMDBSearchResponse>('/discover/movie', {
        params: {
          with_genres: genreId,
          sort_by: 'popularity.desc',
          page
        }
      });
      return response.data.results;
    } catch (error) {
      console.error(`Error obteniendo películas del género ${genreId}:`, error);
      return [];
    }
  }

  /**
   * Verificar si la API está configurada
   */
  isConfigured(): boolean {
    return !!this.apiKey;
  }
}

// Instancia singleton
export const tmdbAPI = new TMDBAPIClient();

// Helpers de utilidad
export const tmdbHelpers = {
  /**
   * Extraer año de título "Película (1999)"
   */
  extractYear(title: string): number | null {
    const match = title.match(/\((\d{4})\)/);
    return match ? parseInt(match[1]) : null;
  },

  /**
   * Limpiar título eliminando año
   */
  cleanTitle(title: string): string {
    return title.replace(/\s*\(\d{4}\)\s*$/, '').trim();
  },

  /**
   * Formatear fecha
   */
  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  },

  /**
   * Formatear rating (0-10 → 0-5 estrellas)
   */
  convertRatingToStars(tmdbRating: number): number {
    return Math.round((tmdbRating / 10) * 5 * 10) / 10; // 7.5/10 → 3.75/5
  }
};

export default tmdbAPI;