import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# PostgreSQL bağlantı URL'si
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgresql-service:5432/student_workflow")

# Veritabanı bağlantısını sağlamak için engine oluşturuyoruz
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# SessionLocal, veritabanı işlemleri için oturum açmamıza olanak tanır
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_connection():
    # Veritabanı bağlantısını başlatıyoruz
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
