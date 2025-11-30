# 🔄 Guía de Reentrenamiento del Modelo

## 📋 Índice

- [Introducción](#introducción)
- [¿Cuándo Reentrenar?](#cuándo-reentrenar)
- [Métodos de Reentrenamiento](#métodos-de-reentrenamiento)
- [Configuración Automática](#configuración-automática)
- [Monitoreo](#monitoreo)
- [Troubleshooting](#troubleshooting)

---

## 📖 Introducción

El sistema incluye **reentrenamiento automático** del modelo SVD, que combina:
- ✅ Dataset original (MovieLens 1M - 1,000,209 ratings)
- ✅ Ratings de la base de datos (usuarios reales de la aplicación)

### ¿Por qué Reentrenar?

**Problema inicial:**
- Usuarios nuevos (no en MovieLens 1M) reciben recomendaciones genéricas
- El modelo ignora sus ratings en la BD

**Solución temporal (híbrida):**
- Usa similitud de películas para usuarios nuevos
- Funciona bien pero no es óptimo

**Solución definitiva (reentrenamiento):**
- Incluye ratings de usuarios reales en el entrenamiento
- Recomendaciones personalizadas basadas en patrones aprendidos
- Mejor precisión (RMSE/MAE)

---

## 🎯 ¿Cuándo Reentrenar?

### Criterios Recomendados

| Situación | Acción |
|-----------|--------|
| **< 100 ratings nuevos** | ❌ No reentrenar (usar lógica híbrida) |
| **100-500 ratings nuevos** | ⚠️ Considerar reentrenamiento semanal |
| **500-1000 ratings nuevos** | ✅ Reentrenamiento recomendado |
| **> 1000 ratings nuevos** | ✅✅ Reentrenamiento necesario |

### Frecuencias Sugeridas

**Desarrollo/Testing:**
```bash
# Reentrenar manualmente cuando pruebes
python retrain_model.py
```

**Producción (bajo tráfico):**
- 🕐 **Semanal**: Domingos a las 2 AM
- 📊 Mínimo: 100 ratings nuevos

**Producción (alto tráfico):**
- 🕐 **Diario**: Cada noche a las 2 AM
- 📊 Mínimo: 50 ratings nuevos

---

## 🛠️ Métodos de Reentrenamiento

### 1️⃣ **Reentrenamiento Manual (Recomendado para Empezar)**

```bash
# Verificar si se necesita
python retrain_model.py --check-only --min-ratings 100

# Reentrenar
python retrain_model.py

# Con parámetros personalizados
python retrain_model.py --factors 150 --epochs 25
```

**Salida esperada:**
```
╔====================================================================╗
║          REENTRENAMIENTO MODELO SVD CON BASE DE DATOS              ║
║                  Sistema de Recomendación - Grupo 8                ║
╚====================================================================╝

======================================================================
PASO 1: Cargando dataset MovieLens 1M original
======================================================================
✓ Dataset original cargado: 1000209 ratings

======================================================================
PASO 2: Cargando ratings de la base de datos
======================================================================
✓ Ratings de BD cargados: 152
  • Usuarios únicos: 23
  • Películas únicas: 87

======================================================================
PASO 3: Combinando datasets
======================================================================
Ratings originales: 1000209
Ratings de BD: 152
✓ Total combinado: 1000361 ratings

======================================================================
PASO 4: Entrenando modelo SVD
======================================================================
Parámetros: n_factors=100, n_epochs=20, lr_all=0.005, reg_all=0.02
...
✓ Modelo entrenado en 610.45 segundos

======================================================================
PASO 5: Evaluando modelo
======================================================================
RMSE: 0.93652
MAE:  0.73801

======================================================================
PASO 6: Exportando modelo
======================================================================
✓ Backup creado: models/svd_model_1m_backup_20251129_183045.pkl
✓ Modelo exportado: models/svd_model_1m.pkl (12.48 MB)
  • Usuarios: 6063
  • Películas: 3706
  • Rating promedio: 3.581

======================================================================
RESUMEN DEL REENTRENAMIENTO
======================================================================
Tiempo de entrenamiento: 610.45 segundos
RMSE: 0.93652
MAE:  0.73801
Ratings de BD añadidos: 152
Modelo exportado: ✓ Sí
Timestamp: 2025-11-29 18:30:45
```

### 2️⃣ **Reentrenamiento desde la API**

Con el servidor corriendo:

```bash
# Verificar estado
curl http://localhost:8000/admin/retrain/check

# Reentrenar
curl -X POST "http://localhost:8000/admin/retrain" \
  -H "Content-Type: application/json" \
  -d '{
    "n_factors": 100,
    "n_epochs": 20,
    "min_new_ratings": 100
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Modelo reentrenado exitosamente y recargado en memoria",
  "training_time": 610.45,
  "metrics": {
    "rmse": 0.93652,
    "mae": 0.73801
  },
  "db_ratings_count": 152,
  "timestamp": "2025-11-29T18:30:45"
}
```

### 3️⃣ **Reentrenamiento Programado (Automático)**

```bash
# Instalar dependencias
pip install schedule

# Ejecución única (para probar)
python schedule_retrain.py --mode once

# Ejecución continua cada 24 horas
python schedule_retrain.py --mode continuous --interval 24

# Ejecución diaria a las 2 AM
python schedule_retrain.py --mode daily --time "02:00"

# Ejecución semanal (domingos a las 2 AM)
python schedule_retrain.py --mode weekly --day sunday --time "02:00"
```

---

## ⚙️ Configuración Automática

### Opción A: Cron (Linux/Mac)

```bash
# Editar crontab
crontab -e

# Añadir línea (cada domingo a las 2 AM)
0 2 * * 0 cd /ruta/a/backend && /ruta/a/.venv/bin/python schedule_retrain.py --mode once --min-ratings 100 >> logs/cron_retrain.log 2>&1
```

**Ejemplos de cron:**

| Frecuencia | Cron | Descripción |
|------------|------|-------------|
| Diario 2 AM | `0 2 * * *` | Cada día a las 2 AM |
| Semanal (Domingo) | `0 2 * * 0` | Cada domingo a las 2 AM |
| Quincenal | `0 2 1,15 * *` | Día 1 y 15 de cada mes |
| Mensual | `0 2 1 * *` | Primer día del mes |

### Opción B: Systemd Service (Linux)

Crear archivo `/etc/systemd/system/retrain-model.service`:

```ini
[Unit]
Description=Movie Recommender Model Retraining
After=network.target

[Service]
Type=simple
User=tu-usuario
WorkingDirectory=/ruta/a/backend
ExecStart=/ruta/a/.venv/bin/python schedule_retrain.py --mode daily --time "02:00"
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Activar:
```bash
sudo systemctl enable retrain-model
sudo systemctl start retrain-model
sudo systemctl status retrain-model
```

### Opción C: Task Scheduler (Windows)

1. Abrir "Programador de tareas"
2. Crear tarea básica
3. Configurar:
   - **Desencadenador**: Semanal, Domingo, 2:00 AM
   - **Acción**: Iniciar programa
   - **Programa**: `C:\Python312\python.exe`
   - **Argumentos**: `schedule_retrain.py --mode once`
   - **Iniciar en**: `C:\ruta\a\backend`

### Opción D: Docker + Cron

`Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# Instalar cron
RUN apt-get update && apt-get install -y cron

# Configurar cron
RUN echo "0 2 * * 0 cd /app && python schedule_retrain.py --mode once" > /etc/cron.d/retrain
RUN chmod 0644 /etc/cron.d/retrain
RUN crontab /etc/cron.d/retrain

CMD cron && uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📊 Monitoreo

### 1. Logs Automáticos

Los logs se guardan en `logs/retrain_schedule.log`:

```bash
# Ver logs en tiempo real
tail -f logs/retrain_schedule.log

# Ver últimas 50 líneas
tail -n 50 logs/retrain_schedule.log

# Buscar errores
grep "ERROR" logs/retrain_schedule.log
```

### 2. Verificar Estado desde la API

```bash
# Estado del reentrenamiento
curl http://localhost:8000/admin/retrain/check

# Salud general del sistema
curl http://localhost:8000/health
```

### 3. Notificaciones (Opcional)

Editar `schedule_retrain.py`, método `_send_notification()`:

**Email:**
```python
def _send_notification(self, result):
    import smtplib
    from email.mime.text import MIMEText
    
    msg = MIMEText(f"""
    Modelo SVD reentrenado exitosamente
    
    RMSE: {result['metrics']['rmse']:.5f}
    MAE: {result['metrics']['mae']:.5f}
    Tiempo: {result['training_time']:.2f}s
    Ratings añadidos: {result['db_ratings_count']}
    """)
    
    msg['Subject'] = '✅ Reentrenamiento Completado'
    msg['From'] = 'tu-email@gmail.com'
    msg['To'] = 'admin@tudominio.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('tu-email@gmail.com', 'tu-contraseña-app')
        server.send_message(msg)
```

**Slack Webhook:**
```python
def _send_notification(self, result):
    import requests
    
    webhook_url = "https://hooks.slack.com/services/TU_WEBHOOK"
    
    message = {
        "text": f"✅ Modelo reentrenado\nRMSE: {result['metrics']['rmse']:.5f}"
    }
    
    requests.post(webhook_url, json=message)
```

---

## 🔍 Verificación Post-Reentrenamiento

### 1. Verificar Modelo Actualizado

```python
import pickle

with open('models/svd_model_1m.pkl', 'rb') as f:
    model_data = pickle.load(f)
    print(f"Usuarios: {model_data['n_users']}")
    print(f"Última actualización: {model_data.get('retrained_at', 'Never')}")
    print(f"Versión: {model_data.get('version', '1.0')}")
```

### 2. Probar Recomendaciones

```bash
# Reiniciar servidor (para cargar modelo actualizado)
# Ctrl+C y luego:
uvicorn main:app --reload

# Probar recomendaciones
curl -X POST "http://localhost:8000/recommendations/from-db" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_nuevo", "n": 5}'
```

### 3. Comparar Métricas

Antes vs Después:
- ✅ RMSE debería mantenerse o mejorar
- ✅ Más usuarios en el trainset
- ✅ Recomendaciones más personalizadas

---

## 🐛 Troubleshooting

### Problema: "No se necesita reentrenar"

**Causa:** Pocos ratings nuevos en BD.

**Solución:**
```bash
# Verificar cuántos ratings hay
curl http://localhost:8000/database/stats

# Forzar reentrenamiento (reducir mínimo)
python retrain_model.py --min-ratings 10
```

### Problema: Modelo no se recarga automáticamente

**Causa:** Servidor no detecta cambios en el modelo.

**Solución:**
```bash
# Opción 1: Reiniciar servidor manualmente
# Ctrl+C y luego:
uvicorn main:app --reload

# Opción 2: Usar endpoint de reentrenamiento (recarga automática)
curl -X POST http://localhost:8000/admin/retrain
```

### Problema: Reentrenamiento muy lento

**Causas:**
- Muchos ratings en BD (>10,000)
- Parámetros altos (n_epochs=50)

**Soluciones:**
```bash
# Reducir épocas temporalmente
python retrain_model.py --epochs 10

# Reducir factores
python retrain_model.py --factors 50 --epochs 15

# Reentrenar en horario de baja demanda
```

### Problema: Error "Database locked"

**Causa:** Servidor usando BD mientras se reentrena.

**Solución:**
```bash
# Opción 1: Usar endpoint (maneja locks automáticamente)
curl -X POST http://localhost:8000/admin/retrain

# Opción 2: Detener servidor temporalmente
# Ctrl+C, reentrenar, reiniciar
```

### Problema: Backup no se crea

**Causa:** Falta espacio en disco.

**Solución:**
```bash
# Ver espacio
df -h

# Limpiar backups antiguos
rm models/svd_model_1m_backup_*.pkl

# Reentrenar sin backup
python retrain_model.py --no-backup
```

---

## 📈 Mejores Prácticas

### ✅ DO's

1. **Hacer backup antes de reentrenar** (activado por defecto)
2. **Reentrenar en horarios de baja demanda** (2-4 AM)
3. **Monitorear logs regularmente**
4. **Verificar métricas después del reentrenamiento**
5. **Empezar con umbral alto** (100+ ratings) y ajustar

### ❌ DON'Ts

1. **NO reentrenar con muy pocos ratings** (<50)
2. **NO reentrenar durante horas pico**
3. **NO ignorar los logs de error**
4. **NO usar --no-backup en producción**
5. **NO reentrenar muy frecuentemente** (max 1x/día)

---

## 🎯 Resumen de Comandos

```bash
# Verificación
python retrain_model.py --check-only
curl http://localhost:8000/admin/retrain/check

# Reentrenamiento Manual
python retrain_model.py
python retrain_model.py --factors 100 --epochs 20

# Reentrenamiento desde API
curl -X POST http://localhost:8000/admin/retrain

# Scheduler
python schedule_retrain.py --mode once
python schedule_retrain.py --mode daily --time "02:00"
python schedule_retrain.py --mode weekly --day sunday

# Monitoreo
tail -f logs/retrain_schedule.log
curl http://localhost:8000/health
```

---

## 📞 Soporte

Si tienes problemas con el reentrenamiento:
1. Revisa los logs: `logs/retrain_schedule.log`
2. Verifica el estado: `curl http://localhost:8000/health`
3. Consulta esta guía
4. Contacta al equipo del Grupo 8

---

**Grupo 8 - Sistemas Inteligentes**  
Fabián González Lence, Diego Hernández Chico, Miguel Martín Falagán