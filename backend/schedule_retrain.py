"""
Script para Reentrenamiento Automático Periódico
Sistema de Recomendación de Películas - Grupo 8

Opciones de uso:
1. Ejecutar manualmente: python schedule_retrain.py
2. Configurar con cron (Linux/Mac):
   0 2 * * 0 cd /path/to/backend && python schedule_retrain.py
   (Cada domingo a las 2 AM)
3. Configurar con Task Scheduler (Windows)
"""

import schedule
import time
import logging
from datetime import datetime
from retrain_model import retrain_model, check_retrain_needed
from database import SessionLocal, Rating

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/retrain_schedule.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class RetrainingScheduler:
    """Planificador de reentrenamiento automático"""
    
    def __init__(
        self,
        min_new_ratings=100,
        n_factors=100,
        n_epochs=20,
        check_interval_hours=24
    ):
        self.min_new_ratings = min_new_ratings
        self.n_factors = n_factors
        self.n_epochs = n_epochs
        self.check_interval_hours = check_interval_hours
        self.last_check = None
        self.last_retrain = None
    
    def check_and_retrain(self):
        """Verifica si se necesita reentrenar y lo ejecuta"""
        logger.info("="*70)
        logger.info("Iniciando verificación de reentrenamiento")
        logger.info("="*70)
        
        self.last_check = datetime.now()
        
        try:
            # Verificar si se necesita
            needs_retrain = check_retrain_needed(self.min_new_ratings)
            
            if needs_retrain:
                logger.info("✓ Se necesita reentrenamiento. Iniciando proceso...")
                
                # Reentrenar
                result = retrain_model(
                    n_factors=self.n_factors,
                    n_epochs=self.n_epochs,
                    backup=True
                )
                
                if result['success']:
                    self.last_retrain = datetime.now()
                    logger.info("✅ Reentrenamiento completado exitosamente")
                    logger.info(f"   RMSE: {result['metrics']['rmse']:.5f}")
                    logger.info(f"   MAE: {result['metrics']['mae']:.5f}")
                    logger.info(f"   Tiempo: {result['training_time']:.2f}s")
                    logger.info(f"   Ratings añadidos: {result['db_ratings_count']}")
                    
                    # Opcional: Enviar notificación (email, Slack, etc.)
                    self._send_notification(result)
                else:
                    logger.error(f"❌ Error en reentrenamiento: {result.get('error')}")
            else:
                logger.info("ℹ️ No se necesita reentrenamiento en este momento")
                
                # Mostrar estadísticas
                db = SessionLocal()
                try:
                    total_ratings = db.query(Rating).count()
                    logger.info(f"   Total ratings en BD: {total_ratings}")
                    logger.info(f"   Mínimo requerido: {self.min_new_ratings}")
                finally:
                    db.close()
        
        except Exception as e:
            logger.error(f"❌ Error durante verificación: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _send_notification(self, result):
        """Envía notificación sobre el reentrenamiento (placeholder)"""
        # Aquí puedes implementar:
        # - Envío de email
        # - Notificación a Slack
        # - Webhook a Discord
        # - etc.
        
        logger.info("📧 Notificación enviada (placeholder)")
        
        # Ejemplo con email (requiere configuración):
        # import smtplib
        # from email.mime.text import MIMEText
        # 
        # msg = MIMEText(f"Modelo reentrenado exitosamente\nRMSE: {result['metrics']['rmse']}")
        # msg['Subject'] = 'Reentrenamiento Modelo SVD Completado'
        # msg['From'] = 'your-email@example.com'
        # msg['To'] = 'admin@example.com'
        # 
        # with smtplib.SMTP('smtp.gmail.com', 587) as server:
        #     server.starttls()
        #     server.login('user', 'password')
        #     server.send_message(msg)
    
    def run_once(self):
        """Ejecuta una sola verificación"""
        logger.info("Modo: Ejecución única")
        self.check_and_retrain()
    
    def run_continuous(self):
        """Ejecuta verificaciones periódicas continuas"""
        logger.info(f"Modo: Ejecución continua cada {self.check_interval_hours} horas")
        
        # Programar tarea
        schedule.every(self.check_interval_hours).hours.do(self.check_and_retrain)
        
        # Ejecutar inmediatamente
        self.check_and_retrain()
        
        # Loop infinito
        logger.info("Scheduler iniciado. Presiona Ctrl+C para detener.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
        except KeyboardInterrupt:
            logger.info("\n⚠️ Scheduler detenido por usuario")
    
    def run_daily_at(self, time_str="02:00"):
        """Ejecuta reentrenamiento diario a una hora específica"""
        logger.info(f"Modo: Ejecución diaria a las {time_str}")
        
        schedule.every().day.at(time_str).do(self.check_and_retrain)
        
        logger.info(f"Scheduler iniciado. Próxima ejecución: {time_str}")
        logger.info("Presiona Ctrl+C para detener.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("\n⚠️ Scheduler detenido por usuario")
    
    def run_weekly(self, day="sunday", time_str="02:00"):
        """Ejecuta reentrenamiento semanal"""
        logger.info(f"Modo: Ejecución semanal cada {day} a las {time_str}")
        
        day_mapping = {
            "monday": schedule.every().monday,
            "tuesday": schedule.every().tuesday,
            "wednesday": schedule.every().wednesday,
            "thursday": schedule.every().thursday,
            "friday": schedule.every().friday,
            "saturday": schedule.every().saturday,
            "sunday": schedule.every().sunday
        }
        
        if day.lower() not in day_mapping:
            logger.error(f"Día inválido: {day}")
            return
        
        day_mapping[day.lower()].at(time_str).do(self.check_and_retrain)
        
        logger.info(f"Scheduler iniciado. Próxima ejecución: {day} {time_str}")
        logger.info("Presiona Ctrl+C para detener.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(3600)  # Verificar cada hora
        except KeyboardInterrupt:
            logger.info("\n⚠️ Scheduler detenido por usuario")


def main():
    """Función principal con CLI"""
    import argparse
    import os
    
    # Crear directorio de logs
    os.makedirs('logs', exist_ok=True)
    
    parser = argparse.ArgumentParser(
        description='Programador de reentrenamiento automático del modelo SVD'
    )
    
    parser.add_argument(
        '--mode',
        choices=['once', 'continuous', 'daily', 'weekly'],
        default='once',
        help='Modo de ejecución'
    )
    
    parser.add_argument(
        '--min-ratings',
        type=int,
        default=100,
        help='Mínimo de ratings nuevos para reentrenar'
    )
    
    parser.add_argument(
        '--factors',
        type=int,
        default=100,
        help='Número de factores latentes'
    )
    
    parser.add_argument(
        '--epochs',
        type=int,
        default=20,
        help='Épocas de entrenamiento'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=24,
        help='Intervalo de verificación en horas (modo continuous)'
    )
    
    parser.add_argument(
        '--time',
        type=str,
        default='02:00',
        help='Hora de ejecución HH:MM (modos daily/weekly)'
    )
    
    parser.add_argument(
        '--day',
        type=str,
        default='sunday',
        choices=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
        help='Día de ejecución (modo weekly)'
    )
    
    args = parser.parse_args()
    
    # Crear scheduler
    scheduler = RetrainingScheduler(
        min_new_ratings=args.min_ratings,
        n_factors=args.factors,
        n_epochs=args.epochs,
        check_interval_hours=args.interval
    )
    
    # Ejecutar según modo
    if args.mode == 'once':
        scheduler.run_once()
    elif args.mode == 'continuous':
        scheduler.run_continuous()
    elif args.mode == 'daily':
        scheduler.run_daily_at(args.time)
    elif args.mode == 'weekly':
        scheduler.run_weekly(args.day, args.time)


if __name__ == "__main__":
    main()