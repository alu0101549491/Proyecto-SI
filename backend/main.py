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

# Importar módulos propios
from database import get_db, create_database, Rating, RatingCRUD, User, UserCRUD
from model_inference_with_db import MovieRecommenderDB

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
        recommender = MovieRecommenderDB('models/svd_model_1m.pkl', movies_path="data/movies.dat")
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

class AddUserRequest(BaseModel):
    user_id: str = Field(..., description="ID del usuario")
    mail: str = Field(..., description="Correo del usuario")
    user_name: str = Field(..., description="Nombre de usuario")
    password: str = Field(..., description="Contraseña")

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

class AddUserResponse(BaseModel):
    user_id: str
    mail: str
    user_name: str
    existing_mail: bool
    existing_user_name: bool

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
        all_users = db.query(User).all()
        unique_users = len(set(user.user_id for user in all_users))
        unique_movies = len(set([r.movie_id for r in all_ratings]))
        
        return DatabaseStatsResponse(
            total_ratings=len(all_ratings),
            total_users=unique_users,
            total_movies_rated=unique_movies,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
@app.post("/users/add", response_model=AddUserResponse)
async def add_user(
    request: AddUserRequest,
    db: Session = Depends(get_db)
):
    """
    Añade un nuevo usuario a la base de datos
    """
    repeated_mail = UserCRUD.get_user_by_mail(db, request.mail)
    if repeated_mail:
      return AddUserResponse(
          user_id="-",
          mail="-",
          user_name="-",
          existing_mail=True,
          existing_user_name=False
      )
    repeated_user_name = UserCRUD.get_user_by_name(db, request.user_name)
    if repeated_user_name:
        return AddUserResponse(
          user_id=repeated_user_name.user_id,
          mail=repeated_user_name.mail,
          user_name=repeated_user_name.user_name,
          existing_mail=False,
          existing_user_name=True
        )
    try:
        new_user = UserCRUD.create_user(db, request.user_id, request.mail, request.user_name, request.password)
        return AddUserResponse(
            user_id=new_user.user_id,
            mail=new_user.mail,
            user_name=new_user.user_name,
            existing_mail=False,
            existing_user_name=False
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
# ENDPOINTS - REENTRENAMIENTO
# ============================================================================

class RetrainRequest(BaseModel):
    n_factors: int = Field(100, ge=10, le=200)
    n_epochs: int = Field(20, ge=5, le=50)
    min_new_ratings: int = Field(100, ge=10)

class RetrainResponse(BaseModel):
    success: bool
    message: str
    training_time: Optional[float] = None
    metrics: Optional[dict] = None
    db_ratings_count: Optional[int] = None
    timestamp: str

@app.post("/admin/retrain", response_model=RetrainResponse)
async def retrain_model_endpoint(
    request: RetrainRequest,
    db: Session = Depends(get_db)
):
    """
    Reentrena el modelo SVD con datos de la base de datos.
    
    ⚠️ ADVERTENCIA: Este proceso puede tomar varios minutos.
    Se recomienda ejecutar cuando haya suficientes ratings nuevos.
    
    Ejemplo:
    ```json
    {
        "n_factors": 100,
        "n_epochs": 20,
        "min_new_ratings": 100
    }
    ```
    """
    from retrain_model import retrain_model, check_retrain_needed
    
    try:
        # Verificar si es necesario reentrenar
        needs_retrain = check_retrain_needed(request.min_new_ratings)
        
        if not needs_retrain:
            total_ratings = db.query(Rating).count()
            return RetrainResponse(
                success=False,
                message=f"No es necesario reentrenar. Solo hay {total_ratings} ratings (mínimo: {request.min_new_ratings})",
                timestamp=datetime.now().isoformat()
            )
        
        # Reentrenar
        result = retrain_model(
            n_factors=request.n_factors,
            n_epochs=request.n_epochs,
            backup=True
        )
        
        if result['success']:
            # Recargar el modelo en memoria
            global recommender
            recommender = MovieRecommenderDB('models/svd_model_1m.pkl', movies_path="data/movies.dat")
            
            return RetrainResponse(
                success=True,
                message="Modelo reentrenado exitosamente y recargado en memoria",
                training_time=result.get('training_time'),
                metrics=result.get('metrics'),
                db_ratings_count=result.get('db_ratings_count'),
                timestamp=result.get('timestamp')
            )
        else:
            return RetrainResponse(
                success=False,
                message=f"Error en reentrenamiento: {result.get('error', 'Unknown')}",
                timestamp=datetime.now().isoformat()
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reentrenando modelo: {str(e)}")


@app.get("/admin/retrain/check")
async def check_retrain_status(
    min_new_ratings: int = 100,
    db: Session = Depends(get_db)
):
    """
    Verifica si es necesario reentrenar el modelo.
    
    Retorna información sobre:
    - Total de ratings en BD
    - Fecha del último reentrenamiento
    - Ratings nuevos desde el último reentrenamiento
    - Si se recomienda reentrenar
    """
    from retrain_model import check_retrain_needed
    import pickle
    import os
    
    try:
        total_ratings = db.query(Rating).count()
        unique_users = len(set([r.user_id for r in db.query(Rating).all()]))
        
        # Info del modelo actual
        model_info = {}
        model_path = 'models/svd_model_1m.pkl'
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
                model_info = {
                    'last_retrain': model_data.get('retrained_at', 'Never (original model)'),
                    'n_users': model_data.get('n_users'),
                    'n_items': model_data.get('n_items'),
                    'version': model_data.get('version', '1.0')
                }
        
        needs_retrain = check_retrain_needed(min_new_ratings)
        
        return {
            "needs_retrain": needs_retrain,
            "database_stats": {
                "total_ratings": total_ratings,
                "unique_users": unique_users,
                "min_required": min_new_ratings
            },
            "current_model": model_info,
            "recommendation": "Retrain recommended" if needs_retrain else "No retrain needed yet",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verificando estado: {str(e)}")


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