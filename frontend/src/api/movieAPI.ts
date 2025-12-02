/**
 * Cliente API para el Backend Python (FastAPI)
 */

import axios, { AxiosInstance } from 'axios';
import {
  RecommendationsResponse,
  AddRatingResponse,
  UserRating,
  PopularMovie
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class MovieAPIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 30000 // 30 segundos
    });
  }

  /**
   * Verificar estado de la API
   */
  async healthCheck() {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      console.error('Error en health check:', error);
      throw error;
    }
  }

  /**
   * Añadir rating y obtener recomendaciones actualizadas
   */
  async addRating(
    userId: string,
    movieId: string,
    rating: number
  ): Promise<AddRatingResponse> {
    try {
      const response = await this.client.post<AddRatingResponse>('/ratings/add', {
        user_id: userId,
        movie_id: movieId,
        rating: rating
      });
      return response.data;
    } catch (error) {
      console.error('Error añadiendo rating:', error);
      throw error;
    }
  }

  /**
   * Obtener historial de ratings del usuario
   */
  async getUserHistory(userId: string): Promise<UserRating[]> {
    try {
      const response = await this.client.get(`/ratings/user/${userId}`);
      return response.data.ratings;
    } catch (error) {
      console.error('Error obteniendo historial:', error);
      return [];
    }
  }

  /**
   * Obtener recomendaciones personalizadas desde BD
   */
  async getRecommendationsFromDB(
    userId: string,
    n: number = 20
  ): Promise<RecommendationsResponse> {
    try {
      const response = await this.client.post<RecommendationsResponse>(
        '/recommendations/from-db',
        {
          user_id: userId,
          n: n
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error obteniendo recomendaciones:', error);
      throw error;
    }
  }

  /**
   * Obtener películas populares (Top 10)
   */
  async getPopularMovies(n: number = 10, minRatings: number = 50) {
    try {
      const response = await this.client.post('/movies/popular', {
        n: n,
        min_ratings: minRatings
      });
      return response.data.movies as PopularMovie[];
    } catch (error) {
      console.error('Error obteniendo populares:', error);
      throw error;
    }
  }

  /**
   * Predecir rating para una película específica
   */
  async predictRating(userId: string, movieId: string): Promise<number> {
    try {
      const response = await this.client.post('/predict', {
        user_id: userId,
        movie_id: movieId
      });
      return response.data.predicted_rating;
    } catch (error) {
      console.error('Error prediciendo rating:', error);
      throw error;
    }
  }

  /**
   * Obtener películas similares
   */
  async getSimilarMovies(movieId: string, n: number = 10) {
    try {
      const response = await this.client.post('/similar-movies', {
        movie_id: movieId,
        n: n
      });
      return response.data.similar_movies;
    } catch (error) {
      console.error('Error obteniendo similares:', error);
      return [];
    }
  }

  /**
   * Eliminar un rating
   */
  async deleteRating(userId: string, movieId: string): Promise<boolean> {
    try {
      await this.client.delete('/ratings/delete', {
        params: {
          user_id: userId,
          movie_id: movieId
        }
      });
      return true;
    } catch (error) {
      console.error('Error eliminando rating:', error);
      return false;
    }
  }

  /**
   * Obtener estadísticas de la base de datos
   */
  async getDatabaseStats() {
    try {
      const response = await this.client.get('/database/stats');
      return response.data;
    } catch (error) {
      console.error('Error obteniendo estadísticas:', error);
      throw error;
    }
  }
}

// Instancia singleton
export const movieAPI = new MovieAPIClient();

export default movieAPI;