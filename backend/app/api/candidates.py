"""
API endpoints for candidate management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database import get_db
from app import models, schemas
from app.utils.file_handler import delete_file
from pathlib import Path

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[schemas.CandidateResponse])
async def list_candidates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all candidates with resume counts
    """
    candidates = db.query(models.Candidate).offset(skip).limit(limit).all()
    
    # Add resume count to each candidate
    result = []
    for candidate in candidates:
        candidate_dict = schemas.CandidateResponse.model_validate(candidate)
        candidate_dict.resume_count = len(candidate.resumes)
        result.append(candidate_dict)
    
    return result


@router.get("/{candidate_id}", response_model=schemas.CandidateDetail)
async def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific candidate with all resumes
    """
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == candidate_id
    ).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with id {candidate_id} not found"
        )
    
    return candidate


@router.post("/", response_model=schemas.CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate: schemas.CandidateCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new candidate
    """
    # Check if email already exists
    if candidate.email:
        existing = db.query(models.Candidate).filter(
            models.Candidate.email == candidate.email
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Candidate with email {candidate.email} already exists"
            )
    
    # Create new candidate
    db_candidate = models.Candidate(**candidate.model_dump())
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    
    logger.info(f"Created candidate: {db_candidate.name} (ID: {db_candidate.id})")
    
    result = schemas.CandidateResponse.model_validate(db_candidate)
    result.resume_count = 0
    
    return result


@router.put("/{candidate_id}", response_model=schemas.CandidateResponse)
async def update_candidate(
    candidate_id: int,
    candidate_update: schemas.CandidateUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a candidate's information
    """
    db_candidate = db.query(models.Candidate).filter(
        models.Candidate.id == candidate_id
    ).first()
    
    if not db_candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with id {candidate_id} not found"
        )
    
    # Update fields
    update_data = candidate_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_candidate, field, value)
    
    db.commit()
    db.refresh(db_candidate)
    
    logger.info(f"Updated candidate: {db_candidate.name} (ID: {db_candidate.id})")
    
    result = schemas.CandidateResponse.model_validate(db_candidate)
    result.resume_count = len(db_candidate.resumes)
    
    return result


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a candidate and all their resumes
    """
    db_candidate = db.query(models.Candidate).filter(
        models.Candidate.id == candidate_id
    ).first()
    
    if not db_candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with id {candidate_id} not found"
        )
    
    # Delete all resume files
    for resume in db_candidate.resumes:
        file_path = Path(resume.file_path)
        delete_file(file_path)
    
    # Delete from database (cascade will delete resumes)
    db.delete(db_candidate)
    db.commit()
    
    logger.info(f"Deleted candidate: {db_candidate.name} (ID: {candidate_id})")
    
    return None


@router.get("/{candidate_id}/resumes", response_model=List[schemas.ResumeResponse])
async def get_candidate_resumes(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all resumes for a specific candidate
    """
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == candidate_id
    ).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with id {candidate_id} not found"
        )
    
    return candidate.resumes
