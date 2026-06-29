"""
API endpoints for searching resumes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
import logging

from app.database import get_db
from app import models, schemas

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=schemas.SearchResponse)
async def search_resumes(
    search_request: schemas.SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search resumes with filters
    """
    query = db.query(models.Resume)
    
    # Text search in multiple fields
    if search_request.query:
        search_term = f"%{search_request.query}%"
        query = query.filter(
            or_(
                models.Resume.resume_name.ilike(search_term),
                models.Resume.raw_text.ilike(search_term),
                models.Resume.role_type.ilike(search_term),
                models.Resume.specialization.ilike(search_term)
            )
        )
    
    # Apply filters
    if search_request.filters:
        filters = search_request.filters
        
        # Experience filter
        if 'min_experience' in filters:
            query = query.filter(
                models.Resume.total_experience >= filters['min_experience']
            )
        
        if 'max_experience' in filters:
            query = query.filter(
                models.Resume.total_experience <= filters['max_experience']
            )
        
        # Skills filter (contains any of the specified skills)
        if 'skills' in filters and filters['skills']:
            # JSON contains filter (SQLite specific)
            skill_filters = []
            for skill in filters['skills']:
                skill_filters.append(models.Resume.skills.contains(skill))
            query = query.filter(or_(*skill_filters))
        
        # Cloud platform filter
        if 'cloud_platforms' in filters and filters['cloud_platforms']:
            cloud_filters = []
            for cloud in filters['cloud_platforms']:
                cloud_filters.append(models.Resume.cloud_platforms.contains(cloud))
            query = query.filter(or_(*cloud_filters))
        
        # Programming language filter
        if 'programming_languages' in filters and filters['programming_languages']:
            lang_filters = []
            for lang in filters['programming_languages']:
                lang_filters.append(models.Resume.programming_languages.contains(lang))
            query = query.filter(or_(*lang_filters))
        
        # Certification filter
        if 'certifications' in filters and filters['certifications']:
            cert_filters = []
            for cert in filters['certifications']:
                cert_filters.append(models.Resume.certifications.contains(cert))
            query = query.filter(or_(*cert_filters))
    
    # Get total count
    total_count = query.count()
    
    # Calculate pagination
    total_pages = (total_count + search_request.page_size - 1) // search_request.page_size
    offset = (search_request.page - 1) * search_request.page_size
    
    # Get paginated results
    resumes = query.offset(offset).limit(search_request.page_size).all()
    
    logger.info(f"Search found {total_count} resumes, returning page {search_request.page}/{total_pages}")
    
    return schemas.SearchResponse(
        total_count=total_count,
        page=search_request.page,
        page_size=search_request.page_size,
        total_pages=total_pages,
        results=[schemas.ResumeResponse.model_validate(r) for r in resumes]
    )


@router.get("/filters/skills", response_model=List[str])
async def get_available_skills(
    db: Session = Depends(get_db)
):
    """
    Get all unique skills across all resumes for filtering
    """
    resumes = db.query(models.Resume).all()
    
    all_skills = set()
    for resume in resumes:
        if resume.skills:
            all_skills.update(resume.skills)
    
    return sorted(list(all_skills))


@router.get("/filters/cloud-platforms", response_model=List[str])
async def get_available_cloud_platforms(
    db: Session = Depends(get_db)
):
    """
    Get all unique cloud platforms for filtering
    """
    resumes = db.query(models.Resume).all()
    
    platforms = set()
    for resume in resumes:
        if resume.cloud_platforms:
            platforms.update(resume.cloud_platforms)
    
    return sorted(list(platforms))


@router.get("/filters/programming-languages", response_model=List[str])
async def get_available_programming_languages(
    db: Session = Depends(get_db)
):
    """
    Get all unique programming languages for filtering
    """
    resumes = db.query(models.Resume).all()
    
    languages = set()
    for resume in resumes:
        if resume.programming_languages:
            languages.update(resume.programming_languages)
    
    return sorted(list(languages))
