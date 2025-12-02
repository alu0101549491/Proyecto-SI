"""
Configuración de Base de Datos SQLite
Sistema de Recomendación de Películas - Grupo 8
"""

from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Crear directorio para la base de datos si no existe
os.makedirs("data", exist_ok=True)

# URL de la base de datos
DATABASE_URL = "sqlite:///./data/movie_recommender.db"

# Crear engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Necesario para SQLite
)

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# ============================================================================
# MODELOS DE LA BASE DE DATOS
# ============================================================================

class Rating(Base):
    """Modelo para almacenar las calificaciones de los usuarios"""
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    movie_id = Column(String, index=True, nullable=False)
    rating = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Rating(user={self.user_id}, movie={self.movie_id}, rating={self.rating})>"


class User(Base):
    """Modelo para almacenar información de usuarios"""
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True, index=True)
    mail = Column(String, unique=True, nullable=False)
    user_name = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, mail={self.mail}, user_name={self.user_name})>"


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def create_database():
    """Crea todas las tablas en la base de datos"""
    Base.metadata.create_all(bind=engine)
    print("✓ Base de datos creada exitosamente")


def get_db():
    """
    Generador de sesiones de base de datos
    Uso en FastAPI con Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_database():
    """Elimina y recrea todas las tablas (CUIDADO: elimina todos los datos)"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✓ Base de datos reiniciada")


# ============================================================================
# OPERACIONES CRUD
# ============================================================================

class RatingCRUD:
    """Operaciones CRUD para ratings"""
    
    @staticmethod
    def create_rating(db, user_id: str, movie_id: str, rating: float):
        """Crea o actualiza un rating"""
        # Verificar si ya existe
        existing = db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.movie_id == movie_id
        ).first()
        
        if existing:
            # Actualizar rating existente
            existing.rating = rating
            existing.timestamp = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Crear nuevo rating
            new_rating = Rating(
                user_id=user_id,
                movie_id=movie_id,
                rating=rating
            )
            db.add(new_rating)
            db.commit()
            db.refresh(new_rating)
            return new_rating
    
    @staticmethod
    def get_user_ratings(db, user_id: str):
        """Obtiene todos los ratings de un usuario"""
        return db.query(Rating).filter(Rating.user_id == user_id).all()
    
    @staticmethod
    def get_movie_ratings(db, movie_id: str):
        """Obtiene todos los ratings de una película"""
        return db.query(Rating).filter(Rating.movie_id == movie_id).all()
    
    @staticmethod
    def get_rating(db, user_id: str, movie_id: str):
        """Obtiene un rating específico"""
        return db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.movie_id == movie_id
        ).first()
    
    @staticmethod
    def delete_rating(db, user_id: str, movie_id: str):
        """Elimina un rating"""
        rating = db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.movie_id == movie_id
        ).first()
        if rating:
            db.delete(rating)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_all_ratings(db, limit: int = None):
        """Obtiene todos los ratings"""
        query = db.query(Rating)
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def count_user_ratings(db, user_id: str):
        """Cuenta cuántas películas ha valorado un usuario"""
        return db.query(Rating).filter(Rating.user_id == user_id).count()


class UserCRUD:
    """Operaciones CRUD para usuarios"""
    
    @staticmethod
    def create_user(db, user_id: str, mail: str, user_name: str, password: str):
        """Crea un nuevo usuario"""
        existing_mail = db.query(User).filter(User.mail == mail).first()
        existing_user_name = db.query(User).filter(User.user_name == user_name).first()
        if existing_mail:
            return existing_mail
        
        if existing_user_name:
            return existing_user_name
        
        new_user = User(user_id=user_id, mail=mail, user_name=user_name, password=password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    
    @staticmethod
    def get_user_by_id(db, user_id: str):
        """Obtiene un usuario"""
        return db.query(User).filter(User.user_id == user_id).first()
    
    @staticmethod
    def get_user_by_name(db, user_name: str):
        return db.query(User).filter(User.user_name == user_name).first()
    
    @staticmethod
    def get_user_by_mail(db, mail: str):
        return db.query(User).filter(User.mail == mail).first()
    
    @staticmethod
    def get_all_users(db):
        """Obtiene todos los usuarios"""
        return db.query(User).all()


# ============================================================================
# INICIALIZACIÓN
# ============================================================================

if __name__ == "__main__":
    print("Creando base de datos...")
    create_database()
    
    # Ejemplo de uso
    db = SessionLocal()
    try:
        # Crear algunos usuarios de prueba
        UserCRUD.create_user(db, "user_1", "manolito@gmail.com", "xXEr_ManolitoXx", "SoyLaCabra")
        UserCRUD.create_user(db, "user_2", "fernando@gmail.com", "Fernando Gutierrez", "Fernando123")
        UserCRUD.create_user(db, "user_3", "willyrex@gmail.com", "W de Willy", "FreeNFTs")

        # Crear algunos ratings de prueba
        RatingCRUD.create_rating(db, "user_1", "1", 5.0)
        RatingCRUD.create_rating(db, "user_1", "260", 4.5)
        RatingCRUD.create_rating(db, "user_2", "1", 4.0)
        
        print("\n✓ Ratings de prueba creados")
        
        # Consultar ratings
        user_ratings = RatingCRUD.get_user_ratings(db, "user_1")
        print(f"\nRatings de user_1: {len(user_ratings)}")
        for rating in user_ratings:
            print(f"  - Película {rating.movie_id}: {rating.rating}⭐")
        
        # Consultar usuarios
        user = UserCRUD.get_user_by_id(db, "user_1")
        print(f"user_id:{user.user_id}, mail:{user.mail}, user_name{user.user_name}, password{user.password}")
    
    finally:
        db.close()