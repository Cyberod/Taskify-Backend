from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create the database engine
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI,
                        pool_pre_ping=True, # to test connections before using them
                        echo=settings.DEBUG, # log SQL queries if DEBUG is True
                        )

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()

# Dependency to get the database session
def get_db():
    """
    Dependency for getting a database session.
    
    Yields:
        SQLAlchemy session
        
    Usage:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

