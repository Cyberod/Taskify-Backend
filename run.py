import uvicorn
import logging
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def main() -> None:
    """
    Run the application using Uvicorn.
    
    This is the main entry point for running the application in development.
    """
    logger.info("Starting Taskify API server")
    
    # Configure Uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        log_level="info",
        workers=1,
    )
    
    logger.info("Taskify API server stopped")

if __name__ == "__main__":
    main()
