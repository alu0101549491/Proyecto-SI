"""
Script para Reentrenar el Modelo SVD con Datos de la Base de Datos
Sistema de Recomendación de Películas - Grupo 8

Este script:
1. Carga el dataset original (MovieLens 1M)
2. Lee los ratings de la base de datos SQLite
3. Combina ambos datasets
4. Reentrena el modelo SVD
5. Exporta el modelo actualizado
"""

import pickle
import time
import os
from datetime import datetime
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
from surprise import accuracy
import pandas as pd

from database import SessionLocal, Rating, RatingCRUD


class ModelRetrainer:
    def __init__(self, original_model_path='models/svd_model_1m.pkl'):
        self.original_model_path = original_model_path
        self.model = None
        self.trainset = None
        self.testset = None
        self.original_data = None
        
    def load_original_movielens_data(self):
        """Carga el dataset MovieLens 1M original"""
        print("="*70)
        print("PASO 1: Cargando dataset MovieLens 1M original")
        print("="*70)
        
        # Cargar desde Surprise
        data = Dataset.load_builtin('ml-1m')
        self.original_data = data
        
        # Obtener estadísticas
        raw_ratings = data.raw_ratings
        print(f"✓ Dataset original cargado: {len(raw_ratings)} ratings")
        
        return data
    
    def load_database_ratings(self):
        """Carga ratings de la base de datos SQLite"""
        print("\n" + "="*70)
        print("PASO 2: Cargando ratings de la base de datos")
        print("="*70)
        
        db = SessionLocal()
        try:
            # Obtener todos los ratings
            db_ratings = RatingCRUD.get_all_ratings(db)
            
            if not db_ratings:
                print("⚠️ No hay ratings en la base de datos")
                return []
            
            # Convertir a formato (user_id, movie_id, rating, timestamp)
            ratings_list = [
                (r.user_id, r.movie_id, float(r.rating), r.timestamp.timestamp())
                for r in db_ratings
            ]
            
            # Estadísticas
            unique_users = len(set([r[0] for r in ratings_list]))
            unique_movies = len(set([r[1] for r in ratings_list]))
            
            print(f"✓ Ratings de BD cargados: {len(ratings_list)}")
            print(f"  • Usuarios únicos: {unique_users}")
            print(f"  • Películas únicas: {unique_movies}")
            
            return ratings_list
        
        finally:
            db.close()
    
    def combine_datasets(self, original_data, db_ratings):
        """Combina el dataset original con los ratings de la BD"""
        print("\n" + "="*70)
        print("PASO 3: Combinando datasets")
        print("="*70)
        
        # Obtener ratings originales
        original_ratings = original_data.raw_ratings
        print(f"Ratings originales: {len(original_ratings)}")
        
        if not db_ratings:
            print("⚠️ Sin ratings de BD, usando solo dataset original")
            return original_data
        
        print(f"Ratings de BD: {len(db_ratings)}")
        
        # Combinar (los ratings de BD se añaden al final)
        combined_ratings = list(original_ratings) + db_ratings
        print(f"✓ Total combinado: {len(combined_ratings)} ratings")
        
        # Crear nuevo dataset de Surprise
        reader = Reader(rating_scale=(1, 5))
        
        # Convertir a DataFrame para Surprise
        df = pd.DataFrame(combined_ratings, columns=['user', 'item', 'rating', 'timestamp'])
        combined_data = Dataset.load_from_df(df[['user', 'item', 'rating']], reader)
        
        return combined_data
    
    def train_model(self, data, n_factors=100, n_epochs=20, lr_all=0.005, reg_all=0.02):
        """Entrena el modelo SVD con el dataset combinado"""
        print("\n" + "="*70)
        print("PASO 4: Entrenando modelo SVD")
        print("="*70)
        
        print(f"Parámetros: n_factors={n_factors}, n_epochs={n_epochs}, "
              f"lr_all={lr_all}, reg_all={reg_all}")
        
        # Inicializar modelo SVD
        self.model = SVD(
            n_factors=n_factors,
            n_epochs=n_epochs,
            lr_all=lr_all,
            reg_all=reg_all,
            random_state=42,
            verbose=True
        )
        
        # Dividir en train y test
        print("\nDividiendo dataset en train (80%) y test (20%)...")
        self.trainset, self.testset = train_test_split(data, test_size=0.2, random_state=42)
        
        # Entrenar
        print("\nIniciando entrenamiento...")
        start_time = time.time()
        
        self.model.fit(self.trainset)
        
        training_time = time.time() - start_time
        print(f"\n✓ Modelo entrenado en {training_time:.2f} segundos")
        
        return training_time
    
    def evaluate_model(self):
        """Evalúa el modelo en el conjunto de test"""
        print("\n" + "="*70)
        print("PASO 5: Evaluando modelo")
        print("="*70)
        
        predictions = self.model.test(self.testset)
        
        rmse = accuracy.rmse(predictions, verbose=False)
        mae = accuracy.mae(predictions, verbose=False)
        
        print(f"\nMétricas de evaluación:")
        print(f"  RMSE: {rmse:.5f}")
        print(f"  MAE:  {mae:.5f}")
        
        return {'rmse': rmse, 'mae': mae}
    
    def export_model(self, filepath='models/svd_model_1m.pkl', backup_original=True):
        """Exporta el modelo reentrenado"""
        print("\n" + "="*70)
        print("PASO 6: Exportando modelo")
        print("="*70)
        
        # Crear backup del modelo original
        if backup_original and os.path.exists(filepath):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = filepath.replace('.pkl', f'_backup_{timestamp}.pkl')
            
            import shutil
            shutil.copy2(filepath, backup_path)
            print(f"✓ Backup creado: {backup_path}")
        
        # Exportar nuevo modelo
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'trainset': self.trainset,
            'n_users': self.trainset.n_users,
            'n_items': self.trainset.n_items,
            'global_mean': self.trainset.global_mean,
            'retrained_at': datetime.now().isoformat(),
            'version': '2.0'
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        file_size = os.path.getsize(filepath) / (1024 * 1024)
        print(f"✓ Modelo exportado: {filepath} ({file_size:.2f} MB)")
        print(f"  • Usuarios: {model_data['n_users']}")
        print(f"  • Películas: {model_data['n_items']}")
        print(f"  • Rating promedio: {model_data['global_mean']:.3f}")
        
        return True


def retrain_model(
    model_path='models/svd_model_1m.pkl',
    n_factors=100,
    n_epochs=20,
    backup=True
):
    """
    Función principal para reentrenar el modelo
    
    Args:
        model_path: Ruta donde guardar el modelo
        n_factors: Número de factores latentes
        n_epochs: Épocas de entrenamiento
        backup: Crear backup del modelo anterior
    
    Returns:
        dict con métricas del reentrenamiento
    """
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*10 + "REENTRENAMIENTO MODELO SVD CON BASE DE DATOS" + " "*14 + "║")
    print("║" + " "*20 + "Sistema de Recomendación - Grupo 8" + " "*14 + "║")
    print("╚" + "="*68 + "╝")
    print()
    
    retrainer = ModelRetrainer(model_path)
    
    try:
        # 1. Cargar dataset original
        original_data = retrainer.load_original_movielens_data()
        
        # 2. Cargar ratings de BD
        db_ratings = retrainer.load_database_ratings()
        
        # 3. Combinar datasets
        combined_data = retrainer.combine_datasets(original_data, db_ratings)
        
        # 4. Entrenar modelo
        training_time = retrainer.train_model(
            combined_data,
            n_factors=n_factors,
            n_epochs=n_epochs
        )
        
        # 5. Evaluar
        metrics = retrainer.evaluate_model()
        
        # 6. Exportar
        success = retrainer.export_model(model_path, backup_original=backup)
        
        # Resumen
        print("\n" + "="*70)
        print("RESUMEN DEL REENTRENAMIENTO")
        print("="*70)
        print(f"Tiempo de entrenamiento: {training_time:.2f} segundos")
        print(f"RMSE: {metrics['rmse']:.5f}")
        print(f"MAE:  {metrics['mae']:.5f}")
        print(f"Ratings de BD añadidos: {len(db_ratings)}")
        print(f"Modelo exportado: {'✓ Sí' if success else '✗ No'}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        return {
            'success': success,
            'training_time': training_time,
            'metrics': metrics,
            'db_ratings_count': len(db_ratings),
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"\n❌ Error durante el reentrenamiento: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }


def check_retrain_needed(min_new_ratings=5):
    """
    Verifica si es necesario reentrenar basándose en nuevos ratings
    
    Args:
        min_new_ratings: Mínimo de ratings nuevos para considerar reentrenamiento
    
    Returns:
        bool: True si se necesita reentrenar
    """
    db = SessionLocal()
    try:
        total_ratings = db.query(Rating).count()
        
        # Leer timestamp del último reentrenamiento
        model_path = 'models/svd_model_1m.pkl'
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
                last_retrain = model_data.get('retrained_at', None)
                
                if last_retrain:
                    print(f"Último reentrenamiento: {last_retrain}")
                    
                    # Contar ratings desde el último reentrenamiento
                    last_retrain_dt = datetime.fromisoformat(last_retrain)
                    new_ratings = db.query(Rating).filter(
                        Rating.timestamp > last_retrain_dt
                    ).count()
                    
                    print(f"Ratings nuevos desde entonces: {new_ratings}")
                    
                    if new_ratings >= min_new_ratings:
                        print(f"✓ Se necesita reentrenamiento ({new_ratings} >= {min_new_ratings})")
                        return True
                    else:
                        print(f"✗ No se necesita reentrenamiento aún ({new_ratings} < {min_new_ratings})")
                        return False
        
        # Si no hay info de reentrenamiento previo, verificar total
        if total_ratings >= min_new_ratings:
            print(f"✓ Se recomienda reentrenamiento inicial ({total_ratings} ratings en BD)")
            return True
        
        return False
    
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Reentrenar modelo SVD con datos de BD')
    parser.add_argument('--factors', type=int, default=100, help='Número de factores latentes')
    parser.add_argument('--epochs', type=int, default=20, help='Épocas de entrenamiento')
    parser.add_argument('--no-backup', action='store_true', help='No crear backup del modelo anterior')
    parser.add_argument('--check-only', action='store_true', help='Solo verificar si se necesita reentrenar')
    parser.add_argument('--min-ratings', type=int, default=100, help='Mínimo de ratings para reentrenar')
    
    args = parser.parse_args()
    
    if args.check_only:
        check_retrain_needed(args.min_ratings)
    else:
        # Verificar primero
        if check_retrain_needed(args.min_ratings):
            result = retrain_model(
                n_factors=args.factors,
                n_epochs=args.epochs,
                backup=not args.no_backup
            )
            
            if result['success']:
                print("\n✅ REENTRENAMIENTO COMPLETADO EXITOSAMENTE")
            else:
                print("\n❌ REENTRENAMIENTO FALLÓ")
        else:
            print("\nℹ️ No es necesario reentrenar en este momento")
            print(f"   Ejecuta con ratings suficientes (mínimo: {args.min_ratings})")