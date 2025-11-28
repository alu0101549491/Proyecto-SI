"""
API Backend con FastAPI para el Sistema de Recomendación de Películas
Grupo 8 - Sistemas Inteligentes
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import pickle
from datetime import datetime

# Importar nuestro sistema de recomendación
from model_inference import MovieRecommender

# Inicializar FastAPI
app = FastAPI(
    title="Movie Recommender API",
    description="API para sistema de recomendación de películas con SVD",
    version="1.0.0"
)

# Configurar CORS para permitir llamadas desde React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # URLs de desarrollo de React/Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar el modelo al iniciar la aplicación
recommender = None

@app.on_event("startup")
async def load_model():
    """Carga el modelo SVD al iniciar el servidor"""
    global recommender
    try:
        recommender = MovieRecommender('models/svd_model_1m.pkl')
        print("✓ Modelo SVD cargado correctamente")
    except Exception as e:
        print(f"✗ Error cargando modelo: {e}")
        raise

# ============================================================================
# MODELOS PYDANTIC (Request/Response)
# ============================================================================

class PredictionRequest(BaseModel):
    user_id: str = Field(..., description="ID del usuario")
    movie_id: str = Field(..., description="ID de la película")

class PredictionResponse(BaseModel):
    user_id: str
    movie_id: str
    predicted_rating: float
    timestamp: str

class RecommendationRequest(BaseModel):
    user_id: str = Field(..., description="ID del usuario")
    n: int = Field(10, ge=1, le=50, description="Número de recomendaciones (1-50)")
    exclude_rated: bool = Field(True, description="Excluir películas ya valoradas")

class MovieRecommendation(BaseModel):
    movie_id: str
    predicted_rating: float
    rank: int

class RecommendationsResponse(BaseModel):
    user_id: str
    recommendations: List[MovieRecommendation]
    count: int
    timestamp: str

class SimilarMoviesRequest(BaseModel):
    movie_id: str = Field(..., description="ID de la película")
    n: int = Field(10, ge=1, le=50, description="Número de películas similares")

class SimilarMovie(BaseModel):
    movie_id: str
    similarity_score: float
    rank: int

class SimilarMoviesResponse(BaseModel):
    source_movie_id: str
    similar_movies: List[SimilarMovie]
    count: int
    timestamp: str

class NewUserRating(BaseModel):
    movie_id: str
    rating: float = Field(..., ge=1.0, le=5.0)

class NewUserRecommendationRequest(BaseModel):
    rated_movies: List[NewUserRating] = Field(..., min_items=1)
    n: int = Field(10, ge=1, le=50)

class PopularMoviesRequest(BaseModel):
    n: int = Field(10, ge=1, le=50)
    min_ratings: int = Field(50, ge=1)

class PopularMovie(BaseModel):
    movie_id: str
    average_rating: float
    rank: int

class PopularMoviesResponse(BaseModel):
    movies: List[PopularMovie]
    count: int
    timestamp: str

class GenreRecommendationRequest(BaseModel):
    user_id: str
    genre: str = Field(..., description="Género de película (Action, Comedy, Drama, etc.)")
    n: int = Field(10, ge=1, le=50)

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    n_users: int
    n_items: int
    global_mean: float
    timestamp: str

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/", response_model=dict)
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Movie Recommender API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Verifica el estado de la API y el modelo"""
    if recommender is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")
    
    return HealthResponse(
        status="healthy",
        model_loaded=True,
        n_users=recommender.n_users,
        n_items=recommender.n_items,
        global_mean=round(recommender.global_mean, 3),
        timestamp=datetime.now().isoformat()
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict_rating(request: PredictionRequest):
    """
    Predice el rating que un usuario daría a una película específica
    
    Ejemplo:
    ```json
    {
        "user_id": "1",
        "movie_id": "1193"
    }
    ```
    """
    if recommender is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    try:
        predicted_rating = recommender.predict_rating(
            request.user_id, 
            request.movie_id
        )
        
        return PredictionResponse(
            user_id=request.user_id,
            movie_id=request.movie_id,
            predicted_rating=round(predicted_rating, 3),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en predicción: {str(e)}")

@app.post("/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Obtiene las top N recomendaciones personalizadas para un usuario
    
    Ejemplo:
    ```json
    {
        "user_id": "1",
        "n": 10,
        "exclude_rated": true
    }
    ```
    """
    if recommender is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    try:
        recommendations = recommender.get_top_n_recommendations(
            user_id=request.user_id,
            n=request.n,
            exclude_rated=request.exclude_rated
        )
        
        movie_recommendations = [
            MovieRecommendation(
                movie_id=movie_id,
                predicted_rating=round(rating, 3),
                rank=i + 1
            )
            for i, (movie_id, rating) in enumerate(recommendations)
        ]
        
        return RecommendationsResponse(
            user_id=request.user_id,
            recommendations=movie_recommendations,
            count=len(movie_recommendations),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error obteniendo recomendaciones: {str(e)}")

@app.post("/similar-movies", response_model=SimilarMoviesResponse)
async def get_similar_movies(request: SimilarMoviesRequest):
    """
    Encuentra películas similares basándose en factores latentes
    
    Ejemplo:
    ```json
    {
        "movie_id": "1",
        "n": 10
    }
    ```
    """
    if recommender is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    try:
        similar_movies = recommender.get_similar_movies(
            movie_id=request.movie_id,
            n=request.n
        )
        
        if not similar_movies:
            raise HTTPException(
                status_code=404, 
                detail=f"Película {request.movie_id} no encontrada"
            )
        
        similar_list = [
            SimilarMovie(
                movie_id=movie_id,
                similarity_score=round(similarity, 3),
                rank=i + 1
            )
            for i, (movie_id, similarity) in enumerate(similar_movies)
        ]
        
        return SimilarMoviesResponse(
            source_movie_id=request.movie_id,
            similar_movies=similar_list,
            count=len(similar_list),
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error buscando similares: {str(e)}")

@app.post("/recommendations/new-user", response_model=RecommendationsResponse)
async def get_new_user_recommendations(request: NewUserRecommendationRequest):
    """
    Genera recomendaciones para un usuario nuevo basándose en ratings iniciales
    
    Ejemplo:
    ```json
    {
        "rated_movies": [
            {"movie_id": "1", "rating": 5.0},
            {"movie_id": "260", "rating": 4.0},
            {"movie_id": "1210", "rating": 4.5}
        ],
        "n": 10
    }
    ```
    """
    if recommender is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    try:
        # Convertir ratings a diccionario
        rated_dict = {
            rating.movie_id: rating.rating 
            for rating in request.rated_movies
        }
        
        recommendations = recommender.get_recommendations_for_new_user(
            rated_movies=rated_dict,
            n=request.n
        )
        
        movie_recommendations = [
            MovieRecommendation(
                movie_id=movie_id,
                predicted_rating=round(score, 3),
                rank=i + 1
            )
            for i, (movie_id, score) in enumerate(recommendations)
        ]
        
        return RecommendationsResponse(
            user_id="new_user",
            recommendations=movie_recommendations,
            count=len(movie_recommendations),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generando recomendaciones: {str(e)}")

@app.post("/movies/popular", response_model=PopularMoviesResponse)
async def get_popular_movies(request: PopularMoviesRequest):
    """
    Obtiene las películas más populares (mejor valoradas con suficientes ratings)
    
    Ejemplo:
    ```json
    {
        "n": 10,
        "min_ratings": 50
    }
    ```
    """
    if recommender is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    try:
        popular_movies = recommender.get_popular_movies(
            n=request.n,
            min_ratings=request.min_ratings
        )
        
        movies_list = [
            PopularMovie(
                movie_id=movie_id,
                average_rating=round(avg_rating, 3),
                rank=i + 1
            )
            for i, (movie_id, avg_rating) in enumerate(popular_movies)
        ]
        
        return PopularMoviesResponse(
            movies=movies_list,
            count=len(movies_list),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error obteniendo populares: {str(e)}")

# ============================================================================
# EJECUTAR SERVIDOR
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",  # Cambiar "main" por el nombre de este archivo
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload durante desarrollo
    )