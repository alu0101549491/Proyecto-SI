# 🎬 Sistema de Recomendación de Películas - Backend con Base de Datos

## 📋 Índice

- [Descripción](#descripción)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Características](#características)
- [Instalación](#instalación)
- [Uso Rápido](#uso-rápido)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [API Endpoints](#api-endpoints)
- [Base de Datos](#base-de-datos)
- [Ejemplos de Uso](#ejemplos-de-uso)
- [Testing](#testing)
- [Despliegue](#despliegue)
- [Troubleshooting](#troubleshooting)

---

## 📖 Descripción

Sistema de recomendación de películas basado en **Filtrado Colaborativo con SVD** (Singular Value Decomposition). El sistema incluye:

- ✅ Modelo SVD entrenado con MovieLens 1M
- ✅ Base de datos SQLite para persistencia
- ✅ API REST con FastAPI
- ✅ Recomendaciones personalizadas en tiempo real
- ✅ Historial de ratings por usuario

**Grupo 8 - Sistemas Inteligentes**  
Fabián González Lence, Diego Hernández Chico, Miguel Martín Falagán

---

## 📁 Estructura del Proyecto

```
backend/
├── models/
│   └── svd_model_1m.pkl          # Modelo entrenado (generado)
├── data/
│   ├── movies.dat                # Metadata de películas (MovieLens)
│   └── movie_recommender.db      # Base de datos SQLite (generado)
├── database.py                    # Configuración de base de datos
├── model_inference_with_db.py    # Sistema de inferencia con BD
├── train_model.py                 # Script de entrenamiento
├── main.py                        # API FastAPI
├── test_database_system.py       # Script de pruebas
├── requirements.txt               # Dependencias Python
├── pyproject.toml                # Configuración uv
└── .env                          # Variables de entorno
```

---

## ✨ Características

### 🎯 Sistema de Recomendación
- Algoritmo SVD (Surprise library)
- Predicciones personalizadas por usuario
- Recomendaciones basadas en películas similares
- Top películas populares

### 💾 Base de Datos
- SQLite para persistencia de datos
- Almacenamiento de ratings por usuario
- Historial completo de calificaciones
- Operaciones CRUD completas

### 🚀 API REST
- FastAPI con documentación automática
- Endpoints para añadir ratings
- Endpoints para obtener recomendaciones
- Integración BD + Modelo en tiempo real
- CORS configurado para frontend

---

## 🔧 Instalación

### Requisitos Previos
- Python 3.12+
- pip o uv (gestor de paquetes)

### 1️⃣ Clonar y Navegar

```bash
cd backend
```

### 2️⃣ Crear Entorno Virtual

```bash
# Con uv (recomendado)
uv venv

# Con venv tradicional
python -m venv .venv
```

### 3️⃣ Activar Entorno Virtual

```bash
# Windows:
.venv\Scripts\activate

# Mac/Linux:
source .venv/bin/activate
```

### 4️⃣ Instalar Dependencias

```bash
# Con uv
uv sync

# Con pip
pip install -r requirements.txt
```

---

## 🚀 Uso Rápido

### Paso 1: Entrenar el Modelo

```bash
python train_model.py
```

**Salida esperada:**
```
======================================================================
ENTRENAMIENTO MODELO SVD - MOVIELENS 1M
======================================================================
Cargando dataset MovieLens 1M...
Dataset cargado correctamente

Iniciando entrenamiento del modelo...
✓ Modelo entrenado exitosamente en 610.23 segundos

Evaluando modelo en conjunto de test...
RMSE: 0.93730
MAE:  0.73876

✓ Modelo exportado exitosamente (12.45 MB)
```

### Paso 2: Probar el Sistema con Base de Datos

```bash
python test_database_system.py
```

Este script:
- ✅ Crea la base de datos
- ✅ Añade ratings de prueba
- ✅ Genera recomendaciones
- ✅ Muestra historial de usuario

### Paso 3: Iniciar el Servidor API

```bash
# Método recomendado
uvicorn main:app --reload

# O directamente
python main.py
```

**La API estará disponible en:**
- 🌐 API: http://localhost:8000
- 📚 Documentación interactiva: http://localhost:8000/docs
- 📖 Documentación alternativa: http://localhost:8000/redoc

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    Cliente (React)                      │
│                  http://localhost:3000                  │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP Requests
                         ↓
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Server (main.py)               │
│                  http://localhost:8000                  │
│                                                         │
│  Endpoints:                                             │
│  • POST /ratings/add                                    │
│  • GET  /ratings/user/{user_id}                         │
│  • POST /recommendations/from-db                        │
│  • GET  /health                                         │
└────────────────────┬───────────────────┬────────────────┘
                     │                   │
                     ↓                   ↓
┌────────────────────────────┐  ┌──────────────────────┐
│  MovieRecommenderDB        │  │  Database (SQLite)   │
│  (model_inference_with_db) │  │  (database.py)       │
│                            │  │                      │
│  • Predicciones SVD        │  │  Tables:             │
│  • Recomendaciones         │  │  • ratings           │
│  • Películas similares     │  │  • users             │
└────────────┬───────────────┘  └──────────────────────┘
             │
             ↓
┌────────────────────────────┐
│  Modelo SVD Entrenado      │
│  (svd_model_1m.pkl)        │
│                            │
│  • 6040 usuarios           │
│  • 3675 películas          │
│  • RMSE: 0.937             │
└────────────────────────────┘
```

---

## 🔌 API Endpoints

### 📊 Estado y Salud

#### `GET /`
Información general de la API.

```bash
curl http://localhost:8000/
```

#### `GET /health`
Estado del sistema (modelo, base de datos, estadísticas).

```bash
curl http://localhost:8000/health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "database_connected": true,
  "total_ratings_in_db": 152,
  "n_users": 6040,
  "n_items": 3675,
  "global_mean": 3.581,
  "timestamp": "2025-11-29T18:30:00"
}
```

---

### ⭐ Gestión de Ratings

#### `POST /ratings/add`
**Añade un rating y devuelve recomendaciones actualizadas.**

**Request:**
```json
{
  "user_id": "user_123",
  "movie_id": "1",
  "rating": 5.0
}
```

**Response:**
```json
{
  "rating_saved": {
    "user_id": "user_123",
    "movie_id": "1",
    "rating": 5.0,
    "movie_title": "Toy Story (1995)",
    "timestamp": "2025-11-29T18:30:00"
  },
  "user_stats": {
    "total_ratings": 1,
    "user_id": "user_123"
  },
  "recommendations": [
    {
      "movie_id": "318",
      "predicted_rating": 4.637,
      "title": "Shawshank Redemption, The (1994)",
      "rank": 1
    }
  ]
}
```

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/ratings/add" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "movie_id": "1",
    "rating": 5.0
  }'
```

#### `GET /ratings/user/{user_id}`
**Obtiene el historial completo de un usuario.**

```bash
curl http://localhost:8000/ratings/user/user_123
```

**Response:**
```json
{
  "user_id": "user_123",
  "total_ratings": 5,
  "ratings": [
    {
      "movie_id": "1",
      "title": "Toy Story (1995)",
      "rating": 5.0,
      "timestamp": "2025-11-29T17:26:46"
    }
  ]
}
```

#### `DELETE /ratings/delete`
**Elimina un rating específico.**

```bash
curl -X DELETE "http://localhost:8000/ratings/delete?user_id=user_123&movie_id=1"
```

---

### 🎬 Recomendaciones

#### `POST /recommendations/from-db`
**Obtiene recomendaciones basadas en ratings de la base de datos.**

**Request:**
```json
{
  "user_id": "user_123",
  "n": 10
}
```

**Response:**
```json
{
  "user_id": "user_123",
  "recommendations": [
    {
      "movie_id": "318",
      "predicted_rating": 4.637,
      "title": "Shawshank Redemption, The (1994)",
      "rank": 1
    }
  ],
  "count": 10,
  "timestamp": "2025-11-29T18:30:00"
}
```

#### `POST /predict`
**Predice el rating que un usuario daría a una película.**

**Request:**
```json
{
  "user_id": "user_123",
  "movie_id": "260"
}
```

**Response:**
```json
{
  "user_id": "user_123",
  "movie_id": "260",
  "movie_title": "Star Wars: Episode IV - A New Hope (1977)",
  "predicted_rating": 4.732,
  "timestamp": "2025-11-29T18:30:00"
}
```

---

### 📈 Estadísticas

#### `GET /database/stats`
**Estadísticas generales de la base de datos.**

```bash
curl http://localhost:8000/database/stats
```

**Response:**
```json
{
  "total_ratings": 152,
  "total_users": 23,
  "total_movies_rated": 87,
  "timestamp": "2025-11-29T18:30:00"
}
```

---

## 💾 Base de Datos

### Esquema SQLite

#### Tabla `ratings`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER | Primary key (auto-increment) |
| `user_id` | STRING | ID del usuario |
| `movie_id` | STRING | ID de la película |
| `rating` | FLOAT | Calificación (1.0-5.0) |
| `timestamp` | DATETIME | Fecha/hora de creación |

**Índices:**
- `user_id` (para búsquedas rápidas por usuario)
- `movie_id` (para búsquedas rápidas por película)

#### Tabla `users` (opcional)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER | Primary key |
| `user_id` | STRING | ID único del usuario |
| `created_at` | DATETIME | Fecha de creación |
| `last_activity` | DATETIME | Última actividad |

### Operaciones CRUD

El archivo `database.py` proporciona:

```python
from database import SessionLocal, RatingCRUD

db = SessionLocal()

# Crear rating
RatingCRUD.create_rating(db, "user_1", "1", 5.0)

# Leer ratings de usuario
ratings = RatingCRUD.get_user_ratings(db, "user_1")

# Actualizar (automático al crear con mismo user_id + movie_id)
RatingCRUD.create_rating(db, "user_1", "1", 4.5)

# Eliminar
RatingCRUD.delete_rating(db, "user_1", "1")

# Contar ratings
count = RatingCRUD.count_user_ratings(db, "user_1")

db.close()
```

---

## 📚 Ejemplos de Uso

### Ejemplo 1: Flujo Completo en Python

```python
from database import SessionLocal, create_database
from model_inference_with_db import MovieRecommenderDB

# 1. Crear base de datos
create_database()

# 2. Inicializar recomendador
recommender = MovieRecommenderDB(
    'models/svd_model_1m.pkl',
    movies_path="data/movies.dat"
)

# 3. Crear sesión
db = SessionLocal()

try:
    # 4. Añadir rating y obtener recomendaciones
    result = recommender.add_rating_and_get_recommendations(
        db=db,
        user_id="user_new",
        movie_id="1",
        rating=5.0,
        n_recommendations=10
    )
    
    # 5. Mostrar resultados
    print(f"Rating guardado: {result['rating_saved']['movie_title']}")
    print(f"\nTop 5 Recomendaciones:")
    for rec in result['recommendations'][:5]:
        print(f"  {rec['rank']}. {rec['title']}: {rec['predicted_rating']}⭐")

finally:
    db.close()
```

### Ejemplo 2: Usar la API desde JavaScript/React

```javascript
// Añadir un rating
async function addRating(userId, movieId, rating) {
  const response = await fetch('http://localhost:8000/ratings/add', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      movie_id: movieId,
      rating: rating
    })
  });
  
  const data = await response.json();
  console.log('Rating guardado:', data.rating_saved);
  console.log('Recomendaciones:', data.recommendations);
  return data;
}

// Obtener historial
async function getUserHistory(userId) {
  const response = await fetch(`http://localhost:8000/ratings/user/${userId}`);
  const data = await response.json();
  console.log(`Usuario ${userId} tiene ${data.total_ratings} ratings`);
  return data.ratings;
}

// Usar
addRating('user_123', '1', 5.0);
getUserHistory('user_123');
```

---

## 🧪 Testing

### Script de Prueba Completo

```bash
python test_database_system.py
```

Este script ejecuta:
1. ✅ Creación de base de datos
2. ✅ Carga del modelo SVD
3. ✅ Simulación de ratings de usuario
4. ✅ Generación de recomendaciones
5. ✅ Consulta de historial
6. ✅ Estadísticas de la BD

### Pruebas Manuales de la API

Con el servidor corriendo:

```bash
# Health check
curl http://localhost:8000/health

# Añadir rating
curl -X POST "http://localhost:8000/ratings/add" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "movie_id": "1", "rating": 5.0}'

# Ver historial
curl http://localhost:8000/ratings/user/test

# Estadísticas
curl http://localhost:8000/database/stats
```

### Pruebas con la Documentación Interactiva

1. Abre http://localhost:8000/docs
2. Explora los endpoints
3. Prueba directamente desde el navegador con "Try it out"

---

## 🚀 Despliegue

### Opción 1: Railway / Render

```bash
# Procfile
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Opción 2: Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build y run
docker build -t movie-recommender .
docker run -p 8000:8000 movie-recommender
```

### Opción 3: AWS EC2 / Google Cloud

```bash
# En el servidor
git clone <repo>
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python train_model.py
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🐛 Troubleshooting

### Error: "Modelo no cargado"

```bash
# Verifica que el modelo existe
ls models/svd_model_1m.pkl

# Si no existe, entrénalo
python train_model.py
```

### Error: CORS

Si el frontend no puede conectar:

```python
# En main.py, añade la URL de tu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://tu-frontend.com"  # Añade aquí
    ],
    ...
)
```

### Error: "Database is locked"

SQLite no maneja bien múltiples escrituras simultáneas:

```python
# Solución: usar timeout más alto
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30}
)
```

### Error: Encoding de películas

Si ves caracteres raros en los títulos:

```python
# En model_inference_with_db.py ya probamos varios encodings
# Si persiste, especifica manualmente:
recommender = MovieRecommenderDB(
    'models/svd_model_1m.pkl',
    movies_path="data/movies.dat"
)
```

---

## 📊 Métricas del Modelo

| Métrica | Valor |
|---------|-------|
| **Algoritmo** | SVD (Surprise) |
| **Dataset** | MovieLens 1M |
| **Usuarios** | 6,040 |
| **Películas** | 3,706 |
| **Ratings** | 1,000,209 |
| **RMSE** | 0.937 |
| **MAE** | 0.739 |
| **Factores latentes** | 100 |
| **Épocas** | 20 |

---

## 🔗 Variables de Entorno

Crea un archivo `.env`:

```env
# Servidor
HOST=0.0.0.0
PORT=8000

# Modelo
MODEL_PATH=models/svd_model_1m.pkl
MOVIES_PATH=data/movies.dat

# Base de datos
DATABASE_URL=sqlite:///./data/movie_recommender.db

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Opcional: Para producción
ENVIRONMENT=production
SECRET_KEY=tu-clave-secreta
```

---

## 🔄 Reentrenamiento del Modelo

El sistema incluye **reentrenamiento automático** que combina:
- ✅ Dataset original (MovieLens 1M)
- ✅ Ratings de usuarios reales (Base de datos SQLite)

### Ventajas del Reentrenamiento

**Antes del reentrenamiento:**
- Usuarios nuevos → Recomendaciones basadas en similitud (heurística)
- Predicciones genéricas

**Después del reentrenamiento:**
- Usuarios nuevos incluidos en el modelo entrenado
- Recomendaciones personalizadas con SVD
- Mejor precisión (RMSE/MAE)

### Métodos de Reentrenamiento

#### 1. Manual (Script)
```bash
# Verificar si se necesita
python retrain_model.py --check-only

# Reentrenar
python retrain_model.py

# Con parámetros personalizados
python retrain_model.py --factors 100 --epochs 20 --min-ratings 100
```

#### 2. API Endpoint
```bash
# Verificar estado
curl http://localhost:8000/admin/retrain/check

# Reentrenar desde API
curl -X POST "http://localhost:8000/admin/retrain" \
  -H "Content-Type: application/json" \
  -d '{"n_factors": 100, "n_epochs": 20, "min_new_ratings": 100}'
```

#### 3. Programado (Automático)
```bash
# Una vez
python schedule_retrain.py --mode once

# Diario a las 2 AM
python schedule_retrain.py --mode daily --time "02:00"

# Semanal (domingos)
python schedule_retrain.py --mode weekly --day sunday --time "02:00"
```

### Configurar Cron (Linux/Mac)
```bash
# Editar crontab
crontab -e

# Añadir (cada domingo a las 2 AM)
0 2 * * 0 cd /ruta/a/backend && python schedule_retrain.py --mode once >> logs/cron.log 2>&1
```

### Cuándo Reentrenar

| Ratings Nuevos | Acción |
|----------------|--------|
| < 100 | ❌ No necesario (usa lógica híbrida) |
| 100-500 | ⚠️ Considerar semanal |
| > 500 | ✅ Reentrenar recomendado |

**Ver guía completa:** [RETRAINING_GUIDE.md](RETRAINING_GUIDE.md)

---

## 📝 Próximos Pasos

- ✅ Paso 1: Entrenar y exportar modelo ✓
- ✅ Paso 2: Importar modelo en la app web ✓
- ✅ Paso 3: Base de datos para usuarios
- ⏳ Paso 4: Interfaz gráfica con ratings
- ⏳ Paso 5: Conectar con API externa (TMDB)

---

## 📞 Contacto

**Grupo 8 - Sistemas Inteligentes**  
- Fabián González Lence
- Diego Hernández Chico
- Miguel Martín Falagán

---

## 📄 Licencia

Este proyecto es parte de un trabajo académico para la asignatura de Sistemas Inteligentes.