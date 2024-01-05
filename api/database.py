from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import api.config as config

### Database file to access and configure postgres
db_host = config.get_db_host()
db_name = config.get_db_name()
db_user = config.get_db_user()
db_pass = config.get_db_password()

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
