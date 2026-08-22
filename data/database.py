
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data.models import Base

DATABASE_URL = "sqlite:///finops.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Creates all tables defined in models.py if they don't exist yet."""
    Base.metadata.create_all(bind=engine)


def get_session():
    """Returns a new database session to run queries."""
    return SessionLocal()


if __name__ == "__main__":
    init_db()
    print("Database initialized: finops.db created with all tables.")