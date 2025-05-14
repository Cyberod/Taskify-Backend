import logging

from app.db.init_db import init_db
from app.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init() -> None:
    """Initialize application with initial data."""
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

def main() -> None:
    """Main entry point for data initialization."""
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")

if __name__ == "__main__":
    main()
