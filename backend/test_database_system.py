"""
Script de Prueba para el Sistema con Base de Datos
Sistema de Recomendación de Películas - Grupo 8
"""

from database import SessionLocal, create_database, RatingCRUD
from model_inference_with_db import MovieRecommenderDB

def test_database_system():
    """Prueba completa del sistema con base de datos"""
    
    print("="*80)
    print("PRUEBA DEL SISTEMA DE RECOMENDACIÓN CON BASE DE DATOS")
    print("="*80)
    
    # Crear base de datos
    print("\n[1/5] Creando base de datos...")
    create_database()
    
    # Inicializar recomendador
    print("\n[2/5] Cargando modelo de recomendación...")
    recommender = MovieRecommenderDB(
        'models/svd_model_1m.pkl',
        movies_path="data/movies.dat"
    )
    
    # Crear sesión de BD
    db = SessionLocal()
    
    try:
        # Simular que un usuario califica varias películas
        print("\n[3/5] Simulando ratings de usuario...")
        print("-" * 80)
        
        test_user = "user_demo"
        test_ratings = [
            ("1", 5.0, "Toy Story"),
            ("260", 5.0, "Star Wars: Episode IV"),
            ("1210", 4.5, "Star Wars: Episode VI"),
            ("480", 4.0, "Jurassic Park"),
            ("589", 4.5, "Terminator 2")
        ]
        
        for movie_id, rating, title in test_ratings:
            RatingCRUD.create_rating(db, test_user, movie_id, rating)
            print(f"  ✓ {title}: {rating}⭐")
        
        # Obtener recomendaciones basadas en la BD
        print("\n[4/5] Generando recomendaciones personalizadas...")
        print("-" * 80)
        
        recommendations = recommender.get_recommendations_from_db(
            db=db,
            user_id=test_user,
            n=10,
            exclude_rated=True
        )
        
        print(f"\n🎬 Top 10 Recomendaciones para {test_user}:")
        print()
        for i, (movie_id, predicted_rating, title) in enumerate(recommendations, 1):
            print(f"  {i}. {title}")
            print(f"     ID: {movie_id} | Rating predicho: {predicted_rating:.3f}⭐")
        
        # Ver historial del usuario
        print("\n[5/5] Historial completo del usuario...")
        print("-" * 80)
        
        history = recommender.get_user_history(db, test_user)
        print(f"\n📊 Historial de {test_user} ({len(history)} películas):")
        print()
        for item in history:
            print(f"  • {item['title']}: {item['rating']}⭐")
            print(f"    Fecha: {item['timestamp']}")
        
        # Estadísticas de la base de datos
        print("\n" + "="*80)
        print("ESTADÍSTICAS DE LA BASE DE DATOS")
        print("="*80)
        
        from database import Rating
        total_ratings_user = RatingCRUD.count_user_ratings(db, test_user)
        all_ratings = db.query(Rating).count()
        unique_users = len(set([r.user_id for r in db.query(Rating).all()]))
        unique_movies = len(set([r.movie_id for r in db.query(Rating).all()]))
        
        print(f"\n  • Total de ratings en BD: {all_ratings}")
        print(f"  • Total de usuarios únicos: {unique_users}")
        print(f"  • Total de películas valoradas: {unique_movies}")
        print(f"  • Ratings del usuario de prueba: {total_ratings_user}")
        
        print("\n" + "="*80)
        print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
        print("="*80)
        
        # Probar añadir rating y obtener recomendaciones en un solo paso
        print("\n" + "="*80)
        print("PRUEBA: Añadir rating y obtener recomendaciones actualizadas")
        print("="*80)
        
        result = recommender.add_rating_and_get_recommendations(
            db=db,
            user_id="user_new",
            movie_id="1",
            rating=5.0,
            n_recommendations=5
        )
        
        print(f"\n✓ Rating guardado:")
        print(f"  Usuario: {result['rating_saved']['user_id']}")
        print(f"  Película: {result['rating_saved']['movie_title']}")
        print(f"  Rating: {result['rating_saved']['rating']}⭐")
        
        print(f"\n🎬 Top 5 Recomendaciones para el nuevo usuario:")
        for rec in result['recommendations']:
            print(f"  {rec['rank']}. {rec['title']}")
            print(f"     Rating predicho: {rec['predicted_rating']}⭐")
        
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
        print("\n✓ Sesión de base de datos cerrada")


def test_api_endpoints():
    """Prueba los endpoints de la API (requiere servidor corriendo)"""
    import requests
    
    print("\n" + "="*80)
    print("PRUEBA DE ENDPOINTS DE LA API")
    print("="*80)
    print("\nNOTA: El servidor debe estar corriendo en http://localhost:8000")
    print("Ejecuta: uvicorn main:app --reload")
    
    base_url = "http://localhost:8000"
    
    # Health check
    print("\n[1/4] Health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("  ✓ API está funcionando")
            print(f"  Ratings en BD: {response.json()['total_ratings_in_db']}")
        else:
            print(f"  ✗ Error: {response.status_code}")
    except Exception as e:
        print(f"  ✗ No se pudo conectar: {e}")
        return
    
    # Añadir rating
    print("\n[2/4] Añadiendo rating...")
    try:
        response = requests.post(
            f"{base_url}/ratings/add",
            json={
                "user_id": "api_test_user",
                "movie_id": "1",
                "rating": 5.0
            }
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Rating guardado: {data['rating_saved']['movie_title']}")
            print(f"  ✓ {len(data['recommendations'])} recomendaciones recibidas")
        else:
            print(f"  ✗ Error: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Obtener historial
    print("\n[3/4] Obteniendo historial de usuario...")
    try:
        response = requests.get(f"{base_url}/ratings/user/api_test_user")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Historial obtenido: {data['total_ratings']} ratings")
        else:
            print(f"  ✗ Error: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Estadísticas de BD
    print("\n[4/4] Estadísticas de base de datos...")
    try:
        response = requests.get(f"{base_url}/database/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Total ratings: {data['total_ratings']}")
            print(f"  ✓ Total usuarios: {data['total_users']}")
            print(f"  ✓ Total películas: {data['total_movies_rated']}")
        else:
            print(f"  ✗ Error: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {e}")


if __name__ == "__main__":
    # Prueba del sistema local
    test_database_system()
    
    # Prueba de la API (comentar si el servidor no está corriendo)
    print("\n\n")
    respuesta = input("¿Probar endpoints de la API? (requiere servidor corriendo) [s/N]: ")
    if respuesta.lower() == 's':
        test_api_endpoints()
    
    print("\n" + "="*80)
    print("TODAS LAS PRUEBAS COMPLETADAS")
    print("="*80)