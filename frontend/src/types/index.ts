/**
 * Tipos TypeScript para el Sistema de Recomendación
 * Grupo 8 - Sistemas Inteligentes
 */

// ============================================================================
// TIPOS DEL BACKEND (API Python)
// ============================================================================

export interface MovieRecommendation {
  movie_id: string;
  predicted_rating: number;
  title: string;
  rank: number;
}

export interface PopularMovie {
  movie_id: string;
  average_rating: number;
  rank: number;
}

export interface UserRating {
  movie_id: string;
  title: string;
  rating: number;
  timestamp: string;
}

export interface RecommendationsResponse {
  user_id: string;
  recommendations: MovieRecommendation[];
  count: number;
  timestamp: string;
}

export interface AddRatingResponse {
  rating_saved: {
    user_id: string;
    movie_id: string;
    rating: number;
    movie_title: string;
    timestamp: string;
  };
  user_stats: {
    total_ratings: number;
    user_id: string;
  };
  recommendations: MovieRecommendation[];
}

// ============================================================================
// TIPOS DE TMDB (The Movie Database)
// ============================================================================

export interface TMDBMovie {
  id: number;
  title: string;
  original_title: string;
  overview: string;
  poster_path: string | null;
  backdrop_path: string | null;
  release_date: string;
  vote_average: number;
  vote_count: number;
  popularity: number;
  genre_ids: number[];
  adult: boolean;
  original_language: string;
  video: boolean;
}

export interface TMDBMovieDetails extends TMDBMovie {
  genres: { id: number; name: string }[];
  runtime: number;
  budget: number;
  revenue: number;
  status: string;
  tagline: string;
  production_companies: {
    id: number;
    name: string;
    logo_path: string | null;
  }[];
  production_countries: {
    iso_3166_1: string;
    name: string;
  }[];
  spoken_languages: {
    iso_639_1: string;
    name: string;
  }[];
}

export interface TMDBSearchResponse {
  page: number;
  results: TMDBMovie[];
  total_pages: number;
  total_results: number;
}

// ============================================================================
// TIPOS COMBINADOS (Frontend)
// ============================================================================

/**
 * Película con información combinada de backend y TMDB
 */
export interface EnrichedMovie {
  // Del backend
  movie_id: string;
  title: string;
  predicted_rating?: number;
  average_rating?: number;
  rank?: number;
  
  // De TMDB
  tmdb_id?: number;
  poster_url?: string;
  backdrop_url?: string;
  overview?: string;
  release_date?: string;
  genres?: string[];
  vote_average?: number;
  
  // Estado local
  user_rating?: number;
  is_loading?: boolean;
}

/**
 * Sección de recomendaciones en la página principal
 */
export interface RecommendationSection {
  title: string;
  movies: EnrichedMovie[];
  type: 'personal' | 'top' | 'discovery';
  color: string;
}

// ============================================================================
// TIPOS DE GÉNEROS (MovieLens → TMDB)
// ============================================================================

export const MOVIELENS_TO_TMDB_GENRES: Record<string, number> = {
  'Action': 28,
  'Adventure': 12,
  'Animation': 16,
  'Children': 10751,
  'Comedy': 35,
  'Crime': 80,
  'Documentary': 99,
  'Drama': 18,
  'Fantasy': 14,
  'Film-Noir': 10752, // No existe en TMDB, usar War
  'Horror': 27,
  'Musical': 10402,
  'Mystery': 9648,
  'Romance': 10749,
  'Sci-Fi': 878,
  'Thriller': 53,
  'War': 10752,
  'Western': 37
};

// ============================================================================
// TIPOS PARA COMPONENTES
// ============================================================================

export interface MovieCardProps {
  movie: EnrichedMovie;
  onRate: (rating: number) => void;
  onClick?: () => void;
}

export interface StarRatingProps {
  rating: number;
  maxRating?: number;
  size?: number;
  onChange?: (rating: number) => void;
  readonly?: boolean;
}

export interface MovieSectionProps {
  title: string;
  movies: EnrichedMovie[];
  color?: string;
  onRate: (movieId: string, rating: number) => void;
  loading?: boolean;
}

// ============================================================================
// TIPOS DE ESTADO DE LA APLICACIÓN
// ============================================================================

export interface AppState {
  currentUser: string;
  personalRecommendations: EnrichedMovie[];
  topMovies: EnrichedMovie[];
  discoveryRecommendations: EnrichedMovie[];
  userRatings: Map<string, number>;
  loading: boolean;
  error: string | null;
}

// ============================================================================
// TIPOS DE HOOKS
// ============================================================================

export interface UseRecommendationsResult {
  recommendations: EnrichedMovie[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export interface UseRatingResult {
  submitRating: (movieId: string, rating: number) => Promise<void>;
  isSubmitting: boolean;
  error: string | null;
}