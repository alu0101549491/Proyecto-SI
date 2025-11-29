"""
Sistema de Inferencia con Base de Datos
Sistema de Recomendación de Películas - Grupo 8
"""

import pickle
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from collections import defaultdict
from sqlalchemy.orm import Session
from database import Rating, RatingCRUD

class MovieRecommenderDB:
    def __init__(self, model_path='models/svd_model_1m.pkl', movies_path: str = None):
        """
        Inicializa el sistema de recomendación con soporte para base de datos
        """
        self.model_path = model_path
        self.model = None
        self.trainset = None
        self.n_users = 0
        self.n_items = 0
        self.global_mean = 0
        self.movies_df = None
        self.movie_id_to_title = {}
        self.movies_path = movies_path
        
        self._load_model()
        self._load_movies_metadata()
  
    def _load_movies_metadata(self):
        """Carga metadata de películas"""
        import os
        encodings_to_try = ["utf-8", "latin-1", "ISO-8859-1", "cp1252"]
        if self.movies_path is None:
            candidates = [
                "data/movies.csv", "data/movies.tsv", "data/movies.dat",
                "datasets/movies.csv", "datasets/movies.tsv", "datasets/movies.dat",
                "ml-1m/movies.dat", "backend/data/movies.csv", "backend/data/movies.dat"
            ]
        else:
            candidates = [self.movies_path]
        
        for p in candidates:
            if not os.path.exists(p):
                continue
            df = None
            for enc in encodings_to_try:
                try:
                    if p.endswith(".tsv"):
                        df = pd.read_csv(p, sep="\t", dtype={"movieId": str}, encoding=enc)
                    elif p.endswith(".dat"):
                        df = pd.read_csv(
                            p, sep="::", engine="python",
                            names=["movieId", "title", "genres"],
                            dtype={"movieId": str}, header=None, encoding=enc
                        )
                    else:
                        df = pd.read_csv(p, dtype={"movieId": str}, encoding=enc)
                    print(f"✓ Metadata leída desde {p} con encoding {enc}")
                    break
                except Exception:
                    continue

            if df is not None:
                if "MovieID" in df.columns:
                    df = df.rename(columns={"MovieID": "movieId"})
                if "movieId" in df.columns and "title" in df.columns:
                    self.movies_df = df
                    self.movie_id_to_title = {
                        str(row["movieId"]): row["title"] for _, row in df.iterrows()
                    }
                    print(f"✓ {len(self.movie_id_to_title)} títulos de películas cargados")
                    return
        
        print("⚠️ No se encontró metadata de películas")
        self.movie_id_to_title = {}
    
    def get_movie_title(self, movie_id: str) -> str:
        """Devuelve el título de una película"""
        movie_id = str(movie_id)
        return self.movie_id_to_title.get(movie_id, f"Movie {movie_id}")
    
    def _load_model(self):
        """Carga el modelo desde archivo pickle"""
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.trainset = model_data['trainset']
            self.n_users = model_data['n_users']
            self.n_items = model_data['n_items']
            self.global_mean = model_data['global_mean']
            
            print(f"✓ Modelo cargado: {self.n_users} usuarios, {self.n_items} películas")
        except Exception as e:
            print(f"Error cargando modelo: {e}")
            raise
    
    def predict_rating(self, user_id: str, movie_id: str) -> float:
        """Predice el rating para un usuario y película"""
        prediction = self.model.predict(str(user_id), str(movie_id))
        return prediction.est
    
    def get_user_ratings_from_db(self, db: Session, user_id: str) -> Dict[str, float]:
        """Obtiene los ratings de un usuario desde la base de datos"""
        ratings = RatingCRUD.get_user_ratings(db, user_id)
        return {r.movie_id: r.rating for r in ratings}
    
    def get_recommendations_from_db(
        self, 
        db: Session,
        user_id: str, 
        n: int = 10,
        exclude_rated: bool = True
    ) -> List[Tuple[str, float, str]]:
        """
        Obtiene recomendaciones basadas en ratings de la base de datos
        
        Returns:
            Lista de tuplas (movie_id, predicted_rating, title)
        """
        # Obtener películas ya valoradas por el usuario
        user_ratings_db = self.get_user_ratings_from_db(db, user_id)
        rated_movie_ids = set(user_ratings_db.keys())
        
        # Obtener todas las películas del sistema
        all_movie_ids = [self.trainset.to_raw_iid(i) for i in range(self.n_items)]
        
        # Filtrar películas no valoradas si se requiere
        if exclude_rated:
            candidate_movies = [mid for mid in all_movie_ids if mid not in rated_movie_ids]
        else:
            candidate_movies = all_movie_ids
        
        # Predecir ratings
        predictions = []
        for movie_id in candidate_movies:
            pred_rating = self.predict_rating(user_id, movie_id)
            title = self.get_movie_title(movie_id)
            predictions.append((movie_id, pred_rating, title))
        
        # Ordenar por rating predicho
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        return predictions[:n]
    
    def add_rating_and_get_recommendations(
        self,
        db: Session,
        user_id: str,
        movie_id: str,
        rating: float,
        n_recommendations: int = 10
    ) -> Dict:
        """
        Añade un rating a la BD y devuelve recomendaciones actualizadas
        
        Returns:
            Dict con información del rating guardado y recomendaciones
        """
        # Guardar rating en la base de datos
        saved_rating = RatingCRUD.create_rating(db, user_id, movie_id, rating)
        
        # Obtener recomendaciones actualizadas
        recommendations = self.get_recommendations_from_db(
            db, user_id, n=n_recommendations, exclude_rated=True
        )
        
        # Contar total de ratings del usuario
        total_ratings = RatingCRUD.count_user_ratings(db, user_id)
        
        return {
            "rating_saved": {
                "user_id": user_id,
                "movie_id": movie_id,
                "rating": rating,
                "movie_title": self.get_movie_title(movie_id),
                "timestamp": saved_rating.timestamp.isoformat()
            },
            "user_stats": {
                "total_ratings": total_ratings,
                "user_id": user_id
            },
            "recommendations": [
                {
                    "movie_id": mid,
                    "predicted_rating": round(pred, 3),
                    "title": title,
                    "rank": i + 1
                }
                for i, (mid, pred, title) in enumerate(recommendations)
            ]
        }
    
    def get_user_history(self, db: Session, user_id: str) -> List[Dict]:
        """Obtiene el historial de ratings de un usuario"""
        ratings = RatingCRUD.get_user_ratings(db, user_id)
        return [
            {
                "movie_id": r.movie_id,
                "title": self.get_movie_title(r.movie_id),
                "rating": r.rating,
                "timestamp": r.timestamp.isoformat()
            }
            for r in ratings
        ]
    
    def get_similar_movies(self, movie_id: str, n: int = 10) -> List[Tuple[str, float]]:
        """Encuentra películas similares (sin cambios)"""
        try:
            movie_inner_id = self.trainset.to_inner_iid(str(movie_id))
            movie_factors = self.model.qi[movie_inner_id]
            
            similarities = []
            for iid in range(self.n_items):
                if iid == movie_inner_id:
                    continue
                
                other_factors = self.model.qi[iid]
                similarity = np.dot(movie_factors, other_factors) / (
                    np.linalg.norm(movie_factors) * np.linalg.norm(other_factors)
                )
                
                other_movie_id = self.trainset.to_raw_iid(iid)
                similarities.append((other_movie_id, similarity))
            
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:n]
        except ValueError:
            return []
    
    def get_popular_movies(self, n: int = 10, min_ratings: int = 50) -> List[Tuple[str, float]]:
        """Obtiene películas populares (sin cambios)"""
        movie_ratings = defaultdict(list)
        
        for uid in range(self.n_users):
            for (iid, rating) in self.trainset.ur[uid]:
                movie_id = self.trainset.to_raw_iid(iid)
                movie_ratings[movie_id].append(rating)
        
        popular_movies = []
        for movie_id, ratings in movie_ratings.items():
            if len(ratings) >= min_ratings:
                avg_rating = np.mean(ratings)
                popular_movies.append((movie_id, avg_rating))
        
        popular_movies.sort(key=lambda x: x[1], reverse=True)
        return popular_movies[:n]


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    from database import SessionLocal, create_database
    
    # Crear base de datos
    create_database()
    
    # Inicializar recomendador
    recommender = MovieRecommenderDB('models/svd_model_1m.pkl', movies_path="data/movies.dat")
    
    # Crear sesión de BD
    db = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print("EJEMPLO: Añadir rating y obtener recomendaciones")
        print("="*70)
        
        # Usuario califica una película
        result = recommender.add_rating_and_get_recommendations(
            db=db,
            user_id="user_test",
            movie_id="1",  # Toy Story
            rating=5.0,
            n_recommendations=5
        )
        
        print(f"\n✓ Rating guardado:")
        print(f"  Usuario: {result['rating_saved']['user_id']}")
        print(f"  Película: {result['rating_saved']['movie_title']}")
        print(f"  Rating: {result['rating_saved']['rating']}⭐")
        
        print(f"\n📊 Estadísticas del usuario:")
        print(f"  Total de películas valoradas: {result['user_stats']['total_ratings']}")
        
        print(f"\n🎬 Top {len(result['recommendations'])} Recomendaciones:")
        for rec in result['recommendations']:
            print(f"  {rec['rank']}. {rec['title']}")
            print(f"     Rating predicho: {rec['predicted_rating']}⭐")
        
        # Ver historial
        print("\n" + "="*70)
        print("HISTORIAL DEL USUARIO")
        print("="*70)
        history = recommender.get_user_history(db, "user_test")
        for item in history:
            print(f"  • {item['title']}: {item['rating']}⭐ ({item['timestamp']})")
    
    finally:
        db.close()