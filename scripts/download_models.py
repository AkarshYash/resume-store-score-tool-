"""
Download required AI models
"""

import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_sentence_transformer():
    """
    Download Sentence Transformer model
    """
    logger.info("Downloading Sentence Transformer model...")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("✓ Sentence Transformer model downloaded successfully")
        return True
    except Exception as e:
        logger.error(f"✗ Error downloading Sentence Transformer: {e}")
        return False


def download_spacy_model():
    """
    Download spaCy model
    """
    logger.info("Downloading spaCy model...")
    try:
        import spacy
        spacy.cli.download("en_core_web_sm")
        logger.info("✓ spaCy model downloaded successfully")
        return True
    except Exception as e:
        logger.error(f"✗ Error downloading spaCy model: {e}")
        logger.info("You can manually download it with: python -m spacy download en_core_web_sm")
        return False


def main():
    """
    Download all required models
    """
    logger.info("=" * 60)
    logger.info("Downloading AI Models for Resume Intelligence Platform")
    logger.info("=" * 60)
    
    success = True
    
    # Download Sentence Transformer
    if not download_sentence_transformer():
        success = False
    
    # Download spaCy
    if not download_spacy_model():
        success = False
    
    logger.info("=" * 60)
    if success:
        logger.info("✓ All models downloaded successfully!")
        logger.info("You can now run: python scripts/setup_database.py")
    else:
        logger.warning("⚠ Some models failed to download")
        logger.info("The application will download them on first use")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
