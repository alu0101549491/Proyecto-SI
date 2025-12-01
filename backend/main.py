"""
API Backend con FastAPI y Base de Datos
Sistema de Recomendación de Películas - Grupo 8
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import os

# Importar módulos propios
from database import get_db, create_database, Rating, RatingCRUD
from model_inference_with_db import MovieRecommenderDB

MODEL_PATH = os.getenv("MODEL_PATH", "models/svd_model_1m.pkl")
MOVIES_PATH = os.getenv("MOVIES_PATH", "data/movies.dat")

# Inicializar FastAPI
app = FastAPI(
    title="Movie Recommender API with Database",
    description="API con sistema de recomendación y persistencia en SQLite",
    version="2.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear la base de datos al iniciar
create_database()

# Cargar el modelo al iniciar
recommender = None

@app.on_event("startup")
async def load_model():
    """Carga el modelo SVD al iniciar el servidor"""
    global recommender
    try:
        recommender = MovieRecommenderDB(MODEL_PATH, movies_path=MOVIES_PATH)
        print("✓ Modelo y base de datos cargados correctamente")
    except Exception as e:
        print(f"✗ Error cargando modelo: {e}")
        raise

# ============================================================================
# MODELOS PYDANTIC (Request/Response)
# ============================================================================

class AddRatingRequest(BaseModel):
    user_id: str = Field(..., description="ID del usuario")
    movie_id: str = Field(..., description="ID de la película")
    rating: float = Field(..., ge=1.0, le=5.0, description="Rating (1-5)")

class RatingResponse(BaseModel):
    user_id: str
    movie_id: str
    rating: float
    movie_title: str
    timestamp: str

class MovieRecommendation(BaseModel):
    movie_id: str
    predicted_rating: float
    title: str
    rank: int

class AddRatingAndRecommendResponse(BaseModel):
    rating_saved: RatingResponse
    user_stats: dict
    recommendations: List[MovieRecommendation]

class UserHistoryItem(BaseModel):
    movie_id: str
    title: str
    rating: float
    timestamp: str

class UserHistoryResponse(BaseModel):
    user_id: str
    total_ratings: int
    ratings: List[UserHistoryItem]

class RecommendationsRequest(BaseModel):
    user_id: str = Field(..., description="ID del usuario")
    n: int = Field(10, ge=1, le=50, description="Número de recomendaciones")

class PredictionRequest(BaseModel):
    user_id: str = Field(..., description="ID del usuario")
    movie_id: str = Field(..., description="ID de la película")

class PredictionResponse(BaseModel):
    user_id: str
    movie_id: str
    movie_title: str
    predicted_rating: float
    timestamp: str

class DatabaseStatsResponse(BaseModel):
    total_ratings: int
    total_users: int
    total_movies_rated: int
    timestamp: str

class PopularMoviesRequest(BaseModel):
    n: int = Field(10, ge=1, le=50, description="Número de películas")
    min_ratings: int = Field(50, ge=1, description="Mínimo de ratings")

class PopularMovieItem(BaseModel):
    movie_id: str
    title: str
    average_rating: float
    rank: int

class PopularMoviesResponse(BaseModel):
    movies: List[PopularMovieItem]
    count: int

class SimilarMoviesRequest(BaseModel):
    movie_id: str = Field(..., description="ID de la película")
    n: int = Field(10, ge=1, le=50, description="Número de similares")

class SimilarMovieItem(BaseModel):
    movie_id: str
    title: str
    similarity_score: float
    predicted_rating: Optional[float] = None

class SimilarMoviesResponse(BaseModel):
    reference_movie_id: str
    reference_movie_title: str
    similar_movies: List[SimilarMovieItem]
    count: int

# ============================================================================
# ENDPOINTS - BASE DE DATOS
# ============================================================================

@app.post("/ratings/add", response_model=AddRatingAndRecommendResponse)
async def add_rating_with_recommendations(
    request: AddRatingRequest,
    db: Session = Depends(get_db)
):
    """
    Añade un rating a la base de datos y devuelve recomendaciones actualizadas
    
    Ejemplo:
    ```json
    {
        "user_id": "user_1",
        "movie_id": "1",
        "rating": 5.0
    }
    ```
    """
    if recommender is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    try:
        result = recommender.add_rating_and_get_recommendations(
            db=db,
            user_id=request.user_id,
            movie_id=request.movie_id,
            rating=request.rating,
            n_recommendations=10
        )
        
        return AddRatingAndRecommendResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


@app.get("/ratings/user/{user_id}", response_model=UserHistoryResponse)
async def get_user_history(user_id: str, db: Session = Depends(get_db)):
    """
    Obtiene el historial completo de ratings de un usuario
    """
    if recommender is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    try:
        ratings = recommender.get_user_history(db, user_id)
        total = len(ratings)
        
        return UserHistoryResponse(
            user_id=user_id,
            total_ratings=total,
            ratings=ratings
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


@app.delete("/ratings/delete")
async def delete_rating(
    user_id: str,
    movie_id: str,
    db: Session = Depends(get_db)
):
    """
    Elimina un rating específico
    """
    try:
        success = RatingCRUD.delete_rating(db, user_id, movie_id)
        if success:
            return {"message": "Rating eliminado exitosamente"}
        else:
            raise HTTPException(status_code=404, detail="Rating no encontrado")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


@app.get("/database/stats", response_model=DatabaseStatsResponse)
async def get_database_stats(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas generales de la base de datos
    """
    try:
        all_ratings = db.query(Rating).all()
        unique_users = len(set([r.user_id for r in all_ratings]))
        unique_movies = len(set([r.movie_id for r in all_ratings]))
        
        return DatabaseStatsResponse(
            total_ratings=len(all_ratings),
            total_users=unique_users,
            total_movies_rated=unique_movies,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


# ============================================================================
# ENDPOINTS - RECOMENDACIONES
# ============================================================================

@app.post("/recommendations/from-db")
async def get_recommendations_from_database(
    request: RecommendationsRequest,
    db: Session = Depends(get_db)
):
    """
    Obtiene recomendaciones basadas en los ratings almacenados en la BD
    """
    if recommender is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    try:
        recommendations = recommender.get_recommendations_from_db(
            db=db,
            user_id=request.user_id,
            n=request.n,
            exclude_rated=True
        )
        
        return {
            "user_id": request.user_id,
            "recommendations": [
                {
                    "movie_id": mid,
                    "predicted_rating": round(pred, 3),
                    "title": title,
                    "rank": i + 1
                }
                for i, (mid, pred, title) in enumerate(recommendations)
            ],
            "count": len(recommendations),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


@app.post("/movies/popular", response_model=PopularMoviesResponse)
async def get_popular_movies(request: PopularMoviesRequest):
    """
    Obtiene las películas más populares basadas en ratings promedio
    """
    if recommender is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    try:
        popular = recommender.get_popular_movies(n=request.n, min_ratings=request.min_ratings)
        
        return PopularMoviesResponse(
            movies=[
                PopularMovieItem(
                    movie_id=movie_id,
                    title=recommender.get_movie_title(movie_id),
                    average_rating=round(avg_rating, 3),
                    rank=i + 1
                )
                for i, (movie_id, avg_rating) in enumerate(popular)
            ],
            count=len(popular)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


@app.post("/similar-movies", response_model=SimilarMoviesResponse)
async def get_similar_movies(request: SimilarMoviesRequest):
    """
    Obtiene películas similares a una película dada basándose en factores latentes
    """
    if recommender is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    try:
        similar = recommender.get_similar_movies(request.movie_id, n=request.n)
        reference_title = recommender.get_movie_title(request.movie_id)
        
        return SimilarMoviesResponse(
            reference_movie_id=request.movie_id,
            reference_movie_title=reference_title,
            similar_movies=[
                SimilarMovieItem(
                    movie_id=movie_id,
                    title=recommender.get_movie_title(movie_id),
                    similarity_score=round(score, 3)
                )
                for movie_id, score in similar
            ],
            count=len(similar)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


@app.post("/predict", response_model=PredictionResponse)
async def predict_rating(request: PredictionRequest):
    """
    Predice el rating que un usuario daría a una película
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
            movie_title=recommender.get_movie_title(request.movie_id),
            predicted_rating=round(predicted_rating, 3),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


# ============================================================================
# ENDPOINTS - UTILIDADES
# ============================================================================

@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Movie Recommender API with Database",
        "version": "2.0.0",
        "features": [
            "Recomendaciones personalizadas con SVD",
            "Base de datos SQLite persistente",
            "Historial de ratings por usuario",
            "Actualización en tiempo real"
        ],
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Verifica el estado de la API, modelo y base de datos"""
    if recommender is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")
    
    try:
        # Verificar BD
        total_ratings = db.query(Rating).count()
        
        return {
            "status": "healthy",
            "model_loaded": True,
            "database_connected": True,
            "total_ratings_in_db": total_ratings,
            "n_users": recommender.n_users,
            "n_items": recommender.n_items,
            "global_mean": round(recommender.global_mean, 3),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error: {str(e)}")


# ============================================================================
# EJECUTAR SERVIDOR
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )