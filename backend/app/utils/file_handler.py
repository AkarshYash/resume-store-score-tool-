"""
File handling utilities for resume uploads and management
"""

import os
import re
import hashlib
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent security issues
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = os.path.basename(filename)
    
    # Replace spaces with underscores
    filename = filename.replace(" ", "_")
    
    # Remove any character that is not alphanumeric, underscore, hyphen, or dot
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    
    # Limit filename length
    name, ext = os.path.splitext(filename)
    max_name_length = settings.MAX_FILENAME_LENGTH - len(ext)
    if len(name) > max_name_length:
        name = name[:max_name_length]
    
    return f"{name}{ext}"


def validate_file(file: UploadFile) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file
    
    Args:
        file: Uploaded file object
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if file exists
    if not file or not file.filename:
        return False, "No file provided"
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        return False, f"File type {file_ext} not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
    
    # Check file size (if available)
    if hasattr(file, 'size') and file.size:
        if file.size > settings.MAX_UPLOAD_SIZE:
            max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            return False, f"File too large. Maximum size: {max_mb}MB"
    
    return True, None


def generate_unique_filename(original_filename: str, candidate_name: str) -> str:
    """
    Generate a unique filename to prevent collisions
    
    Args:
        original_filename: Original uploaded filename
        candidate_name: Name of the candidate
        
    Returns:
        Unique filename
    """
    # Sanitize inputs
    safe_candidate = sanitize_filename(candidate_name.replace(" ", "_"))
    safe_filename = sanitize_filename(original_filename)
    
    # Get file extension
    name, ext = os.path.splitext(safe_filename)
    
    # Create unique identifier using hash of current time
    import time
    unique_id = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:8]
    
    # Construct filename: CandidateName_OriginalName_UniqueID.ext
    unique_filename = f"{safe_candidate}_{name}_{unique_id}{ext}"
    
    return unique_filename


async def save_upload_file(
    file: UploadFile,
    candidate_name: str,
    destination_dir: Optional[Path] = None
) -> Tuple[Path, str]:
    """
    Save uploaded file to disk
    
    Args:
        file: Uploaded file object
        candidate_name: Name of the candidate
        destination_dir: Destination directory (default: settings.UPLOAD_DIR)
        
    Returns:
        Tuple of (file_path, original_filename)
        
    Raises:
        HTTPException: If file validation fails or save fails
    """
    # Validate file
    is_valid, error_msg = validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Set destination directory
    if destination_dir is None:
        destination_dir = settings.UPLOAD_DIR
    
    # Create candidate subdirectory
    candidate_dir = destination_dir / sanitize_filename(candidate_name.replace(" ", "_"))
    candidate_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    unique_filename = generate_unique_filename(file.filename, candidate_name)
    file_path = candidate_dir / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"File saved successfully: {file_path}")
        return file_path, file.filename
        
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


def delete_file(file_path: Path) -> bool:
    """
    Delete a file from disk
    
    Args:
        file_path: Path to file to delete
        
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
            logger.info(f"File deleted: {file_path}")
            return True
        else:
            logger.warning(f"File not found: {file_path}")
            return False
    except Exception as e:
        logger.error(f"Failed to delete file {file_path}: {e}")
        return False


def get_file_info(file_path: Path) -> dict:
    """
    Get information about a file
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary with file information
    """
    if not file_path.exists():
        return {}
    
    stat = file_path.stat()
    
    return {
        "name": file_path.name,
        "size": stat.st_size,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "extension": file_path.suffix,
        "created": stat.st_ctime,
        "modified": stat.st_mtime,
    }


def create_candidate_directory(candidate_name: str) -> Path:
    """
    Create a directory for a candidate's resumes
    
    Args:
        candidate_name: Name of the candidate
        
    Returns:
        Path to created directory
    """
    candidate_dir = settings.UPLOAD_DIR / sanitize_filename(candidate_name.replace(" ", "_"))
    candidate_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created directory: {candidate_dir}")
    return candidate_dir


def list_candidate_files(candidate_name: str) -> list:
    """
    List all files for a candidate
    
    Args:
        candidate_name: Name of the candidate
        
    Returns:
        List of file paths
    """
    candidate_dir = settings.UPLOAD_DIR / sanitize_filename(candidate_name.replace(" ", "_"))
    
    if not candidate_dir.exists():
        return []
    
    files = []
    for file_path in candidate_dir.iterdir():
        if file_path.is_file():
            files.append(file_path)
    
    return files
