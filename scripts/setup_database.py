"""
Database setup script - Initialize the database and create tables
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from app.database import init_db, engine
from app.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_database():
    """
    Initialize database and create all tables
    """
    logger.info("Setting up database...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created successfully")
        
        # Verify tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"✓ Created {len(tables)} tables:")
        for table in tables:
            logger.info(f"  - {table}")
        
        logger.info("\n✓ Database setup complete!")
        logger.info("You can now start the application with: uvicorn app.main:app --reload")
        
    except Exception as e:
        logger.error(f"✗ Error setting up database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    setup_database()
