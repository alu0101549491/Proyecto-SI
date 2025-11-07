# Solución para el error de numpy con surprise
import numpy as np
# Forzar la inicialización correcta de numpy antes de importar surprise
np.float_ = np.float64
np.int_ = np.int64
np.bool_ = np.bool_

import pandas as pd
from surprise import SVD, SVDpp, NMF, SlopeOne, KNNBasic, KNNWithMeans, KNNBaseline
from surprise import CoClustering, BaselineOnly, NormalPredictor
from surprise import Dataset, Reader, accuracy
from surprise.model_selection import train_test_split
import time

# Cargar el dataset MovieLens 100K
print("Cargando dataset MovieLens 100K...")
data = Dataset.load_builtin('ml-100k')

# Dividir en train y test (80-20)
trainset, testset = train_test_split(data, test_size=0.2, random_state=42)

# Definir los algoritmos a comparar
algorithms = {
    'SVD': SVD(),
    'SVD++ (cache_ratings=False)': SVDpp(cache_ratings=False),
    'SVD++ (cache_ratings=True)': SVDpp(cache_ratings=True),
    'NMF': NMF(),
    'Slope One': SlopeOne(),
    'k-NN': KNNBasic(),
    'Centered k-NN': KNNWithMeans(),
    'k-NN Baseline': KNNBaseline(),
    'Co-Clustering': CoClustering(),
    'Baseline': BaselineOnly(),
    'Random': NormalPredictor()
}

# Almacenar resultados
results = []

# Evaluar cada algoritmo
for name, algo in algorithms.items():
    print(f"\n{'='*60}")
    print(f"Evaluando: {name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    # Entrenar el modelo
    algo.fit(trainset)
    
    # Hacer predicciones
    predictions = algo.test(testset)
    
    # Calcular métricas
    rmse = accuracy.rmse(predictions, verbose=False)
    mae = accuracy.mae(predictions, verbose=False)
    
    elapsed_time = time.time() - start_time
    
    # Guardar resultados
    results.append({
        'Algoritmo': name,
        'RMSE': rmse,
        'MAE': mae,
        'Tiempo (segundos)': elapsed_time
    })
    
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE: {mae:.4f}")
    print(f"Tiempo: {elapsed_time:.2f} segundos")

# Crear DataFrame con resultados
df_results = pd.DataFrame(results)

# Ordenar por RMSE
df_results = df_results.sort_values('RMSE')

# Mostrar tabla de resultados
print("\n" + "="*80)
print("RESULTADOS FINALES - COMPARACIÓN DE ALGORITMOS")
print("="*80)
print(df_results.to_string(index=False))

# Guardar resultados en CSV con formato europeo (punto y coma como separador, coma decimal)
df_results.to_csv('resultados_comparacion_algoritmos.csv', index=False, sep=';', decimal=',')
print("\n✓ Resultados guardados en 'resultados_comparacion_algoritmos.csv' (formato europeo)")

# Identificar el mejor algoritmo para cada métrica
print("\n" + "="*80)
print("MEJORES ALGORITMOS POR MÉTRICA")
print("="*80)
best_rmse = df_results.loc[df_results['RMSE'].idxmin()]
best_mae = df_results.loc[df_results['MAE'].idxmin()]
fastest = df_results.loc[df_results['Tiempo (segundos)'].idxmin()]

print(f"\n🏆 Mejor RMSE: {best_rmse['Algoritmo']}")
print(f"   RMSE: {best_rmse['RMSE']:.4f}")

print(f"\n🏆 Mejor MAE: {best_mae['Algoritmo']}")
print(f"   MAE: {best_mae['MAE']:.4f}")

print(f"\n⚡ Más rápido: {fastest['Algoritmo']}")
print(f"   Tiempo: {fastest['Tiempo (segundos)']:.2f} segundos")

# Análisis adicional
print("\n" + "="*80)
print("ANÁLISIS ADICIONAL")
print("="*80)
print(f"\nDiferencia entre mejor y peor RMSE: {df_results['RMSE'].max() - df_results['RMSE'].min():.4f}")
print(f"Diferencia entre mejor y peor MAE: {df_results['MAE'].max() - df_results['MAE'].min():.4f}")
print(f"\nTiempo total de ejecución: {df_results['Tiempo (segundos)'].sum():.2f} segundos")
print(f"Tiempo promedio por algoritmo: {df_results['Tiempo (segundos)'].mean():.2f} segundos")