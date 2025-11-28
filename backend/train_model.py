"""
Script para entrenar y exportar el modelo SVD con MovieLens 1M
Sistema de Recomendación de Películas - Grupo 8
"""

import pickle
import time
from surprise import SVD, Dataset, Reader
from surprise.model_selection import cross_validate, train_test_split
import pandas as pd
import os

class MovieRecommenderTrainer:
    def __init__(self):
        self.model = None
        self.trainset = None
        self.testset = None
        
    def load_movielens_1m(self):
        """
        Carga el dataset MovieLens 1M desde los archivos locales o desde Surprise
        """
        print("Cargando dataset MovieLens 1M...")
        
        # Opción 1: Cargar desde Surprise (descarga automática)
        data = Dataset.load_builtin('ml-1m')
        
        # Opción 2: Si tienes los archivos localmente
        # Descomentar si prefieres usar archivos locales
        """
        reader = Reader(line_format='user item rating timestamp', sep='::', 
                       rating_scale=(1, 5), skip_lines=0)
        data = Dataset.load_from_file('./ml-1m/ratings.dat', reader=reader)
        """
        
        print(f"Dataset cargado correctamente")
        return data
    
    def train_model(self, data, n_factors=100, n_epochs=20, lr_all=0.005, reg_all=0.02):
        """
        Entrena el modelo SVD con los parámetros especificados
        
        Args:
            data: Dataset de Surprise
            n_factors: Número de factores latentes (default: 100)
            n_epochs: Número de épocas de entrenamiento (default: 20)
            lr_all: Learning rate (default: 0.005)
            reg_all: Regularización (default: 0.02)
        """
        print("\nConfigurando modelo SVD...")
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
        
        # Entrenar modelo
        print("\nIniciando entrenamiento del modelo...")
        start_time = time.time()
        
        self.model.fit(self.trainset)
        
        training_time = time.time() - start_time
        print(f"\n✓ Modelo entrenado exitosamente en {training_time:.2f} segundos")
        
        return training_time
    
    def evaluate_model(self):
        """
        Evalúa el modelo en el conjunto de test
        """
        if self.model is None or self.testset is None:
            print("Error: Primero debes entrenar el modelo")
            return None
        
        print("\nEvaluando modelo en conjunto de test...")
        from surprise import accuracy
        
        predictions = self.model.test(self.testset)
        
        rmse = accuracy.rmse(predictions, verbose=False)
        mae = accuracy.mae(predictions, verbose=False)
        
        print(f"\nMétricas de evaluación:")
        print(f"  RMSE: {rmse:.5f}")
        print(f"  MAE:  {mae:.5f}")
        
        return {'rmse': rmse, 'mae': mae}
    
    def cross_validate_model(self, data, cv=5):
        """
        Realiza validación cruzada del modelo (opcional)
        """
        print(f"\nRealizando validación cruzada con {cv} folds...")
        print("(Esto puede tomar varios minutos...)")
        
        results = cross_validate(
            self.model, 
            data, 
            measures=['RMSE', 'MAE'], 
            cv=cv, 
            verbose=True
        )
        
        print(f"\nResultados de validación cruzada:")
        print(f"  RMSE promedio: {results['test_rmse'].mean():.5f} "
              f"(± {results['test_rmse'].std():.5f})")
        print(f"  MAE promedio:  {results['test_mae'].mean():.5f} "
              f"(± {results['test_mae'].std():.5f})")
        
        return results
    
    def export_model(self, filepath='models/svd_model_1m.pkl'):
        """
        Exporta el modelo entrenado a un archivo pickle
        """
        if self.model is None:
            print("Error: No hay modelo para exportar. Entrena el modelo primero.")
            return False
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        print(f"\nExportando modelo a {filepath}...")
        
        # Guardar el modelo completo con información adicional
        model_data = {
            'model': self.model,
            'trainset': self.trainset,
            'n_users': self.trainset.n_users,
            'n_items': self.trainset.n_items,
            'global_mean': self.trainset.global_mean
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
        print(f"✓ Modelo exportado exitosamente ({file_size:.2f} MB)")
        
        return True
    
    def load_model(self, filepath='models/svd_model_1m.pkl'):
        """
        Carga un modelo previamente entrenado
        """
        print(f"\nCargando modelo desde {filepath}...")
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.trainset = model_data['trainset']
        
        print("✓ Modelo cargado exitosamente")
        print(f"  Usuarios en trainset: {model_data['n_users']}")
        print(f"  Películas en trainset: {model_data['n_items']}")
        print(f"  Rating promedio global: {model_data['global_mean']:.3f}")
        
        return model_data
    
    def predict_rating(self, user_id, movie_id):
        """
        Predice el rating para un usuario y película específicos
        """
        if self.model is None:
            print("Error: Primero debes entrenar o cargar un modelo")
            return None
        
        prediction = self.model.predict(user_id, movie_id)
        return prediction

def main():
    """
    Función principal para ejecutar el entrenamiento completo
    """
    print("="*70)
    print("ENTRENAMIENTO MODELO SVD - MOVIELENS 1M")
    print("Sistema de Recomendación de Películas - Grupo 8")
    print("="*70)
    
    # Inicializar trainer
    trainer = MovieRecommenderTrainer()
    
    # 1. Cargar dataset
    data = trainer.load_movielens_1m()
    
    # 2. Entrenar modelo
    training_time = trainer.train_model(
        data,
        n_factors=100,
        n_epochs=20,
        lr_all=0.005,
        reg_all=0.02
    )
    
    # 3. Evaluar modelo
    metrics = trainer.evaluate_model()
    
    # 4. Exportar modelo
    success = trainer.export_model('models/svd_model_1m.pkl')
    
    # Resumen final
    print("\n" + "="*70)
    print("RESUMEN DEL ENTRENAMIENTO")
    print("="*70)
    print(f"Tiempo de entrenamiento: {training_time:.2f} segundos")
    print(f"RMSE: {metrics['rmse']:.5f}")
    print(f"MAE:  {metrics['mae']:.5f}")
    print(f"Modelo exportado: {'✓ Sí' if success else '✗ No'}")
    print("="*70)
    
    # Ejemplo de predicción
    print("\nEjemplo de predicción:")
    prediction = trainer.predict_rating(user_id='1', movie_id='1')
    print(f"Usuario 1, Película 1: Rating predicho = {prediction.est:.3f}")
    print(f"(Rating real si existe: {prediction.r_ui if prediction.r_ui is not None else 'N/A'})")
    
    return trainer

if __name__ == "__main__":
    trainer = main()