# 🎬 Sistema de Recomendación de Películas - Guía de Setup (Primeros Pasos para Integración del BackEnd)

## 📁 Estructura del Proyecto

```
movie-recommender/
├── backend/
│   ├── models/
│   │   └── svd_model_1m.pkl          # Modelo entrenado (generado)
│   ├── train_model.py                 # Script de entrenamiento
│   ├── model_inference.py             # Sistema de inferencia
│   ├── main.py                        # API FastAPI
│   ├── requirements.txt               # Dependencias Python
│   └── .env                           # Variables de entorno
│
└── frontend/
    ├── src/
    │   ├── api/
    │   │   └── movieAPI.ts            # Cliente API TypeScript
    │   ├── hooks/
    │   │   └── useRecommendations.ts  # Hooks personalizados
    │   └── components/
    │       └── RecommendationList.tsx # Componentes React
    ├── package.json
    └── .env                           # Variables de entorno React
```

---

## 🐍 Backend (Python + FastAPI)

### 1️⃣ Instalación

```bash
cd backend

# Crear entorno virtual (recomendado)
uv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Instalar dependencias
uv sync
```

### 2️⃣ Entrenar el Modelo

```bash
# Ejecutar el entrenamiento (toma unos minutos)
python train_model.py
```

**Salida esperada:**
```
======================================================================
ENTRENAMIENTO MODELO SVD - MOVIELENS 1M
======================================================================
Cargando dataset MovieLens 1M...
Dataset cargado correctamente

Configurando modelo SVD...
Parámetros: n_factors=100, n_epochs=20, lr_all=0.005, reg_all=0.02

Dividiendo dataset en train (80%) y test (20%)...

Iniciando entrenamiento del modelo...
Processing epoch 0
Processing epoch 1
...
✓ Modelo entrenado exitosamente en 610.23 segundos

Evaluando modelo en conjunto de test...
RMSE: 0.93730
MAE:  0.73876

Exportando modelo a models/svd_model_1m.pkl...
✓ Modelo exportado exitosamente (12.45 MB)

======================================================================
RESUMEN DEL ENTRENAMIENTO
======================================================================
Tiempo de entrenamiento: 610.23 segundos
RMSE: 0.93730
MAE:  0.73876
Modelo exportado: ✓ Sí
======================================================================
```

### 3️⃣ Iniciar el Servidor API

```bash
# Método 1: Con uvicorn directamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Método 2: Ejecutando el script
python main.py
```

**La API estará disponible en:**
- 🌐 API: http://localhost:8000
- 📚 Documentación interactiva: http://localhost:8000/docs
- 📖 Documentación alternativa: http://localhost:8000/redoc

### 4️⃣ Variables de Entorno (Backend)

Crear archivo `backend/.env`:

```env
# Configuración del servidor
HOST=0.0.0.0
PORT=8000

# Ruta del modelo
MODEL_PATH=models/svd_model_1m.pkl

# CORS (URLs permitidas del frontend)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Base de datos (para paso 3 del roadmap)
DATABASE_URL=sqlite:///./movie_recommender.db
```

---

## ⚛️ Frontend (React + TypeScript)

### 1️⃣ Instalación

```bash
cd frontend

# Con npm
npm install

# Con yarn
yarn install

# Con pnpm
pnpm install
```

### 2️⃣ Variables de Entorno (Frontend)

Crear archivo `frontend/.env`:

```env
# URL del backend
REACT_APP_API_URL=http://localhost:8000

# Si usas Vite en lugar de Create React App:
VITE_API_URL=http://localhost:8000
```

### 3️⃣ Iniciar el Desarrollo

```bash
# Con Create React App
npm start

# Con Vite
npm run dev
```

**La aplicación estará disponible en:**
- 🌐 React: http://localhost:3000 (CRA) o http://localhost:5173 (Vite)

---

## 🔌 Ejemplos de Uso de la API

### 📡 Desde el Navegador / Postman

#### 1. Health Check
```http
GET http://localhost:8000/health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "n_users": 6040,
  "n_items": 3706,
  "global_mean": 3.581,
  "timestamp": "2024-11-28T10:30:00"
}
```

#### 2. Obtener Recomendaciones
```http
POST http://localhost:8000/recommendations
Content-Type: application/json

{
  "user_id": "1",
  "n": 10,
  "exclude_rated": true
}
```

**Respuesta:**
```json
{
  "user_id": "1",
  "recommendations": [
    {
      "movie_id": "1193",
      "predicted_rating": 4.823,
      "rank": 1
    },
    {
      "movie_id": "2019",
      "predicted_rating": 4.756,
      "rank": 2
    }
  ],
  "count": 10,
  "timestamp": "2024-11-28T10:30:00"
}
```

#### 3. Predecir Rating
```http
POST http://localhost:8000/predict
Content-Type: application/json

{
  "user_id": "1",
  "movie_id": "1193"
}
```

#### 4. Películas Similares
```http
POST http://localhost:8000/similar-movies
Content-Type: application/json

{
  "movie_id": "1",
  "n": 10
}
```

#### 5. Películas Populares
```http
POST http://localhost:8000/movies/popular
Content-Type: application/json

{
  "n": 10,
  "min_ratings": 50
}
```

#### 6. Recomendaciones para Usuario Nuevo
```http
POST http://localhost:8000/recommendations/new-user
Content-Type: application/json

{
  "rated_movies": [
    {"movie_id": "1", "rating": 5.0},
    {"movie_id": "260", "rating": 4.0},
    {"movie_id": "1210", "rating": 4.5}
  ],
  "n": 10
}
```

---

### 💻 Desde React/TypeScript

#### Ejemplo 1: Componente Simple
```tsx
import { useRecommendations } from './api/movieAPI';

function RecommendationList({ userId }: { userId: string }) {
  const { recommendations, loading, error } = useRecommendations(userId, 10);

  if (loading) return <div>Cargando...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <ul>
      {recommendations.map((rec) => (
        <li key={rec.movie_id}>
          Película {rec.movie_id} - ⭐ {rec.predicted_rating.toFixed(2)}
        </li>
      ))}
    </ul>
  );
}
```

#### Ejemplo 2: Uso Directo
```tsx
import { movieAPI } from './api/movieAPI';

async function fetchData() {
  try {
    // Obtener recomendaciones
    const recs = await movieAPI.getRecommendations({
      user_id: '1',
      n: 10
    });
    console.log(recs);

    // Películas populares
    const popular = await movieAPI.getPopularMovies({ n: 10 });
    console.log(popular);

  } catch (error) {
    console.error('Error:', error);
  }
}
```

#### Ejemplo 3: Con useState
```tsx
import { useState, useEffect } from 'react';
import { movieAPI, MovieRecommendation } from './api/movieAPI';

function MyComponent() {
  const [recommendations, setRecommendations] = useState<MovieRecommendation[]>([]);

  useEffect(() => {
    movieAPI.getRecommendations({ user_id: '1', n: 10 })
      .then(response => setRecommendations(response.recommendations))
      .catch(error => console.error(error));
  }, []);

  return (
    <div>
      {recommendations.map(rec => (
        <div key={rec.movie_id}>{rec.movie_id}</div>
      ))}
    </div>
  );
}
```

---

## 🧪 Testing

### Test del Backend
```bash
cd backend

# Probar el sistema de inferencia
python model_inference.py

# Probar la API (con el servidor corriendo)
curl http://localhost:8000/health
```

### Test del Cliente API
```bash
cd frontend

# Ejecutar tests (si los tienes configurados)
npm test
```

---

## 🚀 Despliegue

### Backend
- **Opción 1:** Render, Railway, Fly.io
- **Opción 2:** AWS EC2 / Google Cloud
- **Opción 3:** Docker

```dockerfile
# Dockerfile ejemplo
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend
- **Opción 1:** Vercel, Netlify
- **Opción 2:** GitHub Pages
- **Opción 3:** AWS S3 + CloudFront

---

## 📊 Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Info de la API |
| GET | `/health` | Estado del servidor y modelo |
| POST | `/predict` | Predecir rating individual |
| POST | `/recommendations` | Recomendaciones personalizadas |
| POST | `/similar-movies` | Películas similares |
| POST | `/recommendations/new-user` | Recomendaciones para nuevo usuario |
| POST | `/movies/popular` | Top películas populares |

---

## 🐛 Troubleshooting

### Error: "Modelo no cargado"
```bash
# Verifica que el modelo existe
ls backend/models/svd_model_1m.pkl

# Si no existe, entrena el modelo
python train_model.py
```

### Error: CORS
```python
# En main.py, verifica que tu URL de frontend está en allow_origins
allow_origins=["http://localhost:3000", "http://localhost:5173"]
```

### Error: "Cannot connect to API"
```typescript
// Verifica la URL en .env
REACT_APP_API_URL=http://localhost:8000
```

---

## 📚 Próximos Pasos del Roadmap

- ✅ **Paso 1:** Entrenar y exportar modelo ✓
- ✅ **Paso 2:** Importar modelo en la app web ✓
- ⏳ **Paso 3:** Base de datos para usuarios
- ⏳ **Paso 4:** Interfaz gráfica con ratings
- ⏳ **Paso 5:** Conectar con API externa (TMDB)

---

## 🤝 Contribuciones

Grupo 8: Fabián González Lence, Diego Hernández Chico, Miguel Martín Falagán