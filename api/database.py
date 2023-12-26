from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from os import environ

### Database file to access and configure postgres
db_host = environ.get("DB_HOST")
db_name = environ.get("DB_NAME")
db_user = environ.get("DB_USER")
db_pass = environ.get("DB_PASS")

SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}/{db_name}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)  # , connect_args={"check_same_thread": False} for sqlite
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
