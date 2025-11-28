"""
Sistema de Inferencia para el Modelo SVD
Para usar en el backend/API de producción
"""

import pickle
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from collections import defaultdict

class MovieRecommender:
    def __init__(self, model_path='models/svd_model_1m.pkl', movies_path: str = None):
        """
        Inicializa el sistema de recomendación cargando el modelo entrenado
        
        Args:
            model_path: Ruta al archivo del modelo pickle
            movies_path: Ruta opcional al CSV/TSV con metadata de películas (debe contener movieId y title)
        """
        self.model_path = model_path
        self.model = None
        self.trainset = None
        self.n_users = 0
        self.n_items = 0
        self.global_mean = 0

        # metadata de películas
        self.movies_df = None
        self.movie_id_to_title = {}
        self.movies_path = movies_path
        
        self._load_model()
        # intentar cargar metadata de películas después de cargar el trainset
        self._load_movies_metadata()
  
    def _load_movies_metadata(self):
        """Carga un CSV/TSV/.dat con columnas movieId y title y construye un mapeo movieId -> title
        Ahora soporta el formato MovieLens 1M 'movies.dat' (MovieID::Title::Genres) y prueba varios encodings.
        """
        import os
        encodings_to_try = ["utf-8", "latin-1", "ISO-8859-1", "cp1252"]
        if self.movies_path is None:
            # intentar rutas comunes dentro del proyecto
            candidates = [
                "data/movies.csv",
                "data/movies.tsv",
                "data/movies.dat",
                "datasets/movies.csv",
                "datasets/movies.tsv",
                "datasets/movies.dat",
                "ml-1m/movies.dat",
                "backend/data/movies.csv",
                "backend/data/movies.dat",
            ]
        else:
            candidates = [self.movies_path]
        
        for p in candidates:
            if not os.path.exists(p):
                continue
            df = None
            last_error = None
            # intentar lecturas según extensión, probando varios encodings
            for enc in encodings_to_try:
                try:
                    if p.endswith(".tsv"):
                        df = pd.read_csv(p, sep="\t", dtype={"movieId": str}, encoding=enc)
                    elif p.endswith(".dat"):
                        # MovieLens 1M usa '::' como separador: MovieID::Title::Genres
                        df = pd.read_csv(
                            p,
                            sep="::",
                            engine="python",
                            names=["movieId", "title", "genres"],
                            dtype={"movieId": str},
                            header=None,
                            encoding=enc,
                        )
                    else:
                        df = pd.read_csv(p, dtype={"movieId": str}, encoding=enc)
                    # si llegamos aquí, la lectura fue exitosa
                    print(f"✓ Leído {p} con encoding {enc}")
                    break
                except UnicodeDecodeError as ude:
                    last_error = ude
                    # probar siguiente encoding
                    continue
                except Exception as e:
                    last_error = e
                    # si no es un problema de encoding, intentar siguientes encodings también
                    continue

            if df is None:
                print(f"⚠️ Error leyendo metadata desde {p}: {last_error}")
                continue

            # Aceptar columnas alternativas: MovieID o movieId
            if "movieId" not in df.columns and "MovieID" in df.columns:
                df = df.rename(columns={"MovieID": "movieId"})

            if "movieId" in df.columns and "title" in df.columns:
                self.movies_df = df
                # normalizar keys como str
                self.movie_id_to_title = {
                    str(row["movieId"]): row["title"] for _, row in df.iterrows()
                }
                print(f"✓ Metadata de películas cargada desde {p} ({len(self.movie_id_to_title)} entradas)")
                return
            else:
                print(f"⚠️ Archivo {p} leído pero no contiene las columnas esperadas ('movieId','title').")
                continue

        # fallback: mapping vacío
        print("⚠️ Metadata de películas no encontrada. Se mostrará solo movie_id como título si no hay mapeo.")
        self.movie_id_to_title = {}
    
    def get_movie_title(self, movie_id: str) -> str:
        """Devuelve el título correspondiente al movie_id o un texto por defecto si no está disponible"""
        movie_id = str(movie_id)
        return self.movie_id_to_title.get(movie_id, f"Unknown Title ({movie_id})")
    
    def _load_model(self):
        """Carga el modelo desde el archivo pickle"""
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
        """
        Predice el rating que un usuario daría a una película
        
        Args:
            user_id: ID del usuario
            movie_id: ID de la película
            
        Returns:
            Rating predicho (1-5)
        """
        prediction = self.model.predict(str(user_id), str(movie_id))
        return prediction.est
    
    def get_top_n_recommendations(
        self, 
        user_id: str, 
        n: int = 10,
        exclude_rated: bool = True
    ) -> List[Tuple[str, float]]:
        """
        Obtiene las top N recomendaciones para un usuario
        
        Args:
            user_id: ID del usuario
            n: Número de recomendaciones
            exclude_rated: Si True, excluye películas ya valoradas por el usuario
            
        Returns:
            Lista de tuplas (movie_id, predicted_rating) ordenadas por rating
        """
        # Obtener todas las películas
        all_movie_ids = [self.trainset.to_raw_iid(i) for i in range(self.n_items)]
        
        # Si queremos excluir películas ya valoradas
        if exclude_rated:
            try:
                # Obtener películas ya valoradas por el usuario
                rated_movies = set()
                user_inner_id = self.trainset.to_inner_uid(str(user_id))
                rated_movies = set([
                    self.trainset.to_raw_iid(iid) 
                    for (iid, _) in self.trainset.ur[user_inner_id]
                ])
                all_movie_ids = [mid for mid in all_movie_ids if mid not in rated_movies]
            except ValueError:
                # Usuario nuevo, no tiene películas valoradas
                pass
        
        # Predecir ratings para todas las películas
        predictions = []
        for movie_id in all_movie_ids:
            pred_rating = self.predict_rating(user_id, movie_id)
            predictions.append((movie_id, pred_rating))
        
        # Ordenar por rating predicho (descendente) y tomar top N
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        return predictions[:n]
    
    def get_similar_movies(
        self, 
        movie_id: str, 
        n: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Encuentra películas similares basándose en los factores latentes
        
        Args:
            movie_id: ID de la película
            n: Número de películas similares a retornar
            
        Returns:
            Lista de tuplas (movie_id, similarity_score)
        """
        try:
            # Obtener el vector de factores latentes de la película
            movie_inner_id = self.trainset.to_inner_iid(str(movie_id))
            movie_factors = self.model.qi[movie_inner_id]
            
            # Calcular similitud con todas las demás películas
            similarities = []
            for iid in range(self.n_items):
                if iid == movie_inner_id:
                    continue
                
                other_factors = self.model.qi[iid]
                # Similitud del coseno
                similarity = np.dot(movie_factors, other_factors) / (
                    np.linalg.norm(movie_factors) * np.linalg.norm(other_factors)
                )
                
                other_movie_id = self.trainset.to_raw_iid(iid)
                similarities.append((other_movie_id, similarity))
            
            # Ordenar por similitud (descendente)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return similarities[:n]
        except ValueError:
            # Película no encontrada en el trainset
            return []
    
    def get_recommendations_for_new_user(
        self,
        rated_movies: Dict[str, float],
        n: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Genera recomendaciones para un usuario nuevo basándose en sus ratings iniciales
        
        Args:
            rated_movies: Diccionario {movie_id: rating}
            n: Número de recomendaciones
            
        Returns:
            Lista de tuplas (movie_id, predicted_rating)
        """
        # Para usuarios nuevos, podemos usar películas similares a las que valoraron bien
        recommendations = defaultdict(list)
        
        for movie_id, rating in rated_movies.items():
            if rating >= 4.0:  # Solo considerar películas que le gustaron
                similar_movies = self.get_similar_movies(movie_id, n=20)
                
                for sim_movie_id, similarity in similar_movies:
                    if sim_movie_id not in rated_movies:
                        # Ponderar por el rating dado y la similitud
                        score = rating * similarity
                        recommendations[sim_movie_id].append(score)
        
        # Promediar scores de películas que aparecen múltiples veces
        final_recommendations = [
            (movie_id, np.mean(scores))
            for movie_id, scores in recommendations.items()
        ]
        
        # Ordenar y retornar top N
        final_recommendations.sort(key=lambda x: x[1], reverse=True)
        return final_recommendations[:n]
    
    def get_popular_movies(self, n: int = 10, min_ratings: int = 50) -> List[Tuple[str, float]]:
        """
        Obtiene las películas más populares (mejor valoradas con suficientes ratings)
        
        Args:
            n: Número de películas a retornar
            min_ratings: Mínimo número de ratings que debe tener una película
            
        Returns:
            Lista de tuplas (movie_id, average_rating)
        """
        movie_ratings = defaultdict(list)
        
        # Recopilar todos los ratings por película
        for uid in range(self.n_users):
            for (iid, rating) in self.trainset.ur[uid]:
                movie_id = self.trainset.to_raw_iid(iid)
                movie_ratings[movie_id].append(rating)
        
        # Calcular rating promedio para películas con suficientes valoraciones
        popular_movies = []
        for movie_id, ratings in movie_ratings.items():
            if len(ratings) >= min_ratings:
                avg_rating = np.mean(ratings)
                popular_movies.append((movie_id, avg_rating))
        
        # Ordenar por rating promedio
        popular_movies.sort(key=lambda x: x[1], reverse=True)
        
        return popular_movies[:n]
    
    def get_recommendations_by_genre(
        self,
        user_id: str,
        genre: str,
        movies_df: pd.DataFrame,
        n: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Obtiene recomendaciones filtradas por género
        
        Args:
            user_id: ID del usuario
            genre: Género a filtrar
            movies_df: DataFrame con información de películas (debe tener 'movieId' y 'genres')
            n: Número de recomendaciones
            
        Returns:
            Lista de tuplas (movie_id, predicted_rating)
        """
        # Filtrar películas por género
        genre_movies = movies_df[
            movies_df['genres'].str.contains(genre, case=False, na=False)
        ]['movieId'].astype(str).tolist()
        
        # Predecir ratings solo para películas del género
        predictions = []
        for movie_id in genre_movies:
            pred_rating = self.predict_rating(user_id, movie_id)
            predictions.append((movie_id, pred_rating))
        
        # Ordenar y retornar top N
        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:n]

# Ejemplo de uso
if __name__ == "__main__":
    # Inicializar el recomendador (puedes pasar la ruta al CSV de películas si la tienes)
    recommender = MovieRecommender('models/svd_model_1m.pkl', movies_path="data/movies.dat")
    
    # Ejemplo 1: Predecir un rating específico
    print("\n=== Ejemplo 1: Predicción de Rating ===")
    user_id = "1"
    movie_id = "1193"  # One Flew Over the Cuckoo's Nest
    rating = recommender.predict_rating(user_id, movie_id)
    title = recommender.get_movie_title(movie_id)
    print(f"Rating predicho para Usuario {user_id}, Película {movie_id} - {title}: {rating:.3f}")
    
    # Ejemplo 2: Top 10 recomendaciones para un usuario
    print("\n=== Ejemplo 2: Top 10 Recomendaciones ===")
    recommendations = recommender.get_top_n_recommendations(user_id="1", n=10)
    for i, (movie_id, rating) in enumerate(recommendations, 1):
        title = recommender.get_movie_title(movie_id)
        print(f"{i}. Película {movie_id} - {title}: Rating predicho = {rating:.3f}")
    
    # Ejemplo 3: Películas similares
    print("\n=== Ejemplo 3: Películas Similares ===")
    similar = recommender.get_similar_movies(movie_id="1", n=5)
    for i, (movie_id, similarity) in enumerate(similar, 1):
        title = recommender.get_movie_title(movie_id)
        print(f"{i}. Película {movie_id} - {title}: Similitud = {similarity:.3f}")
    
    # Ejemplo 4: Películas populares
    print("\n=== Ejemplo 4: Top Películas Populares ===")
    popular = recommender.get_popular_movies(n=10)
    for i, (movie_id, avg_rating) in enumerate(popular, 1):
        title = recommender.get_movie_title(movie_id)
        print(f"{i}. Película {movie_id} - {title}: Rating promedio = {avg_rating:.3f}")
    
    # Ejemplo 5: Recomendaciones para usuario nuevo
    print("\n=== Ejemplo 5: Usuario Nuevo ===")
    new_user_ratings = {
        "1": 5.0,      # Toy Story
        "260": 4.0,    # Star Wars
        "1210": 4.5    # Star Wars: Episode VI
    }
    new_recommendations = recommender.get_recommendations_for_new_user(
        new_user_ratings, 
        n=10
    )
    for i, (movie_id, score) in enumerate(new_recommendations, 1):
        title = recommender.get_movie_title(movie_id)
        print(f"{i}. Película {movie_id} - {title}: Score = {score:.3f}")