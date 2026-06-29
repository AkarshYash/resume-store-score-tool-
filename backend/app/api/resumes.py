"""
API endpoints for resume management
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import tempfile
import logging

from app.database import get_db
from app import models, schemas
from app.utils.file_handler import save_upload_file, delete_file, get_file_info
from app.services.resume_parser import ResumeParser

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[schemas.ResumeResponse])
async def list_resumes(
    skip: int = 0,
    limit: int = 100,
    candidate_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    List all resumes with optional candidate filter
    """
    query = db.query(models.Resume)
    
    if candidate_id:
        query = query.filter(models.Resume.candidate_id == candidate_id)
    
    resumes = query.offset(skip).limit(limit).all()
    return resumes


@router.get("/all/detailed", response_model=List[schemas.ResumeWithCandidate])
async def list_all_resumes_detailed(
    skip: int = 0,
    limit: int = 500,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List ALL resumes from ALL candidates with full details
    """
    query = db.query(models.Resume).join(models.Candidate)
    
    if search:
        query = query.filter(
            (models.Resume.resume_name.contains(search)) |
            (models.Candidate.name.contains(search)) |
            (models.Resume.skills.contains(search))
        )
    
    resumes = query.order_by(models.Resume.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for resume in resumes:
        resume_data = {
            **{k: v for k, v in resume.__dict__.items() if not k.startswith('_')},
            'candidate_name': resume.candidate.name if resume.candidate else "Unknown",
            'candidate_email': resume.candidate.email if resume.candidate else None
        }
        result.append(schemas.ResumeWithCandidate(**resume_data))
    
    return result


@router.post("/extract-names", response_model=List[schemas.ExtractedFileName])
async def extract_names_from_filenames(
    filenames: List[str]
):
    """
    Extract resume names from filenames
    Example: "Nirav_Python_GenAI_Resume.pdf" -> "Python GenAI Resume"
    """
    results = []
    
    for filename in filenames:
        # Remove extension
        name_without_ext = Path(filename).stem
        
        # Remove common prefixes (candidate names, dates, etc.)
        # Split by underscore or space
        parts = name_without_ext.replace('_', ' ').replace('-', ' ').split()
        
        # Remove common words
        filtered_parts = [p for p in parts if p.lower() not in ['resume', 'cv', 'updated', 'final', 'new', 'latest']]
        
        # If first part looks like a name (starts with capital), remove it
        if filtered_parts and filtered_parts[0][0].isupper() and len(filtered_parts) > 1:
            # Check if it might be a candidate name (short word, all caps or title case)
            if len(filtered_parts[0]) < 15 and not any(char.islower() for char in filtered_parts[0][1:]):
                filtered_parts = filtered_parts[1:]
        
        suggested_name = ' '.join(filtered_parts) if filtered_parts else name_without_ext
        
        results.append(schemas.ExtractedFileName(
            original_filename=filename,
            suggested_name=suggested_name,
            full_name_without_ext=name_without_ext
        ))
    
    return results


@router.post("/suggest-names", response_model=List[schemas.ExtractedFileName])
async def suggest_names_from_files(
    files: List[UploadFile] = File(...)
):
    """
    Read selected resume files and suggest editable resume titles before upload.
    """
    results = []

    for file in files:
        suffix = Path(file.filename or "").suffix
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(await file.read())
                temp_path = Path(temp_file.name)

            text = ResumeParser.extract_text(temp_path)
            suggested_name = ResumeParser.infer_resume_title(file.filename or "Resume", text)
            results.append(schemas.ExtractedFileName(
                original_filename=file.filename or "Resume",
                suggested_name=suggested_name,
                full_name_without_ext=Path(file.filename or "Resume").stem
            ))
        except Exception as e:
            logger.warning(f"Could not inspect {file.filename}: {e}")
            fallback = ResumeParser.infer_resume_title(file.filename or "Resume")
            results.append(schemas.ExtractedFileName(
                original_filename=file.filename or "Resume",
                suggested_name=fallback,
                full_name_without_ext=Path(file.filename or "Resume").stem
            ))
        finally:
            if temp_path and temp_path.exists():
                temp_path.unlink(missing_ok=True)

    return results


@router.get("/{resume_id}", response_model=schemas.ResumeDetail)
async def get_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific resume with all details
    """
    resume = db.query(models.Resume).filter(
        models.Resume.id == resume_id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with id {resume_id} not found"
        )
    
    # Add candidate name
    result = schemas.ResumeDetail.model_validate(resume)
    result.candidate_name = resume.candidate.name if resume.candidate else None
    
    return result


from fastapi.responses import FileResponse

@router.get("/{resume_id}/file")
async def get_resume_file(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the actual resume file for viewing
    """
    db_resume = db.query(models.Resume).filter(
        models.Resume.id == resume_id
    ).first()
    
    if not db_resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    file_path = Path(db_resume.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
        
    return FileResponse(
        path=file_path, 
        filename=db_resume.file_name,
        media_type="application/pdf" if db_resume.file_type.lower() == "pdf" else "application/octet-stream"
    )


@router.post("/upload", response_model=schemas.FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    candidate_id: int = Form(...),
    resume_name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a resume file for a candidate
    """
    # Verify candidate exists
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == candidate_id
    ).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with id {candidate_id} not found"
        )
    
    try:
        # Save file
        file_path, original_filename = await save_upload_file(file, candidate.name)
        
        # Get file info
        file_info = get_file_info(file_path)
        
        # Parse resume
        logger.info(f"Parsing resume: {original_filename}")
        parsed_data = ResumeParser.parse_resume(file_path)
        if not resume_name.strip():
            resume_name = ResumeParser.infer_resume_title(original_filename, parsed_data.get('raw_text') or "")
        
        # Create resume record
        db_resume = models.Resume(
            candidate_id=candidate_id,
            resume_name=resume_name,
            file_name=original_filename,
            file_path=str(file_path),
            file_type=file_info['extension'],
            file_size=file_info['size'],
            raw_text=parsed_data.get('raw_text'),
            email=parsed_data.get('email'),
            phone=parsed_data.get('phone'),
            total_experience=parsed_data.get('total_experience'),
            skills=parsed_data.get('skills', []),
            programming_languages=parsed_data.get('programming_languages', []),
            frameworks=parsed_data.get('frameworks', []),
            databases=parsed_data.get('databases', []),
            cloud_platforms=parsed_data.get('cloud_platforms', []),
            devops_tools=parsed_data.get('devops_tools', []),
            ai_ml_skills=parsed_data.get('ai_ml_skills', []),
            certifications=parsed_data.get('certifications', []),
            companies=parsed_data.get('companies', []),
        )
        
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)
        
        logger.info(f"Resume uploaded successfully: {resume_name} (ID: {db_resume.id})")
        
        return schemas.FileUploadResponse(
            success=True,
            message=f"Resume '{resume_name}' uploaded and parsed successfully",
            resume_id=db_resume.id,
            file_name=original_filename
        )
        
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload resume: {str(e)}"
        )


@router.post("/batch-upload", response_model=schemas.BatchUploadResponse)
async def batch_upload_resumes(
    candidate_id: int = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload multiple resume files for a candidate
    """
    # Verify candidate exists
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == candidate_id
    ).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with id {candidate_id} not found"
        )
    
    results = []
    successful = 0
    failed = 0
    
    for file in files:
        try:
            # Extract resume name from filename (without extension)
            resume_name = Path(file.filename).stem
            
            # Save and parse
            file_path, original_filename = await save_upload_file(file, candidate.name)
            file_info = get_file_info(file_path)
            parsed_data = ResumeParser.parse_resume(file_path)
            
            # Create resume record
            db_resume = models.Resume(
                candidate_id=candidate_id,
                resume_name=resume_name,
                file_name=original_filename,
                file_path=str(file_path),
                file_type=file_info['extension'],
                file_size=file_info['size'],
                raw_text=parsed_data.get('raw_text'),
                email=parsed_data.get('email'),
                phone=parsed_data.get('phone'),
                total_experience=parsed_data.get('total_experience'),
                skills=parsed_data.get('skills', []),
                programming_languages=parsed_data.get('programming_languages', []),
                frameworks=parsed_data.get('frameworks', []),
                databases=parsed_data.get('databases', []),
                cloud_platforms=parsed_data.get('cloud_platforms', []),
                devops_tools=parsed_data.get('devops_tools', []),
                ai_ml_skills=parsed_data.get('ai_ml_skills', []),
                certifications=parsed_data.get('certifications', []),
                companies=parsed_data.get('companies', []),
            )
            
            db.add(db_resume)
            db.commit()
            db.refresh(db_resume)
            
            results.append(schemas.FileUploadResponse(
                success=True,
                message=f"Uploaded successfully",
                resume_id=db_resume.id,
                file_name=original_filename
            ))
            successful += 1
            
        except Exception as e:
            logger.error(f"Error uploading {file.filename}: {e}")
            results.append(schemas.FileUploadResponse(
                success=False,
                message=f"Failed: {str(e)}",
                file_name=file.filename
            ))
            failed += 1
    
    return schemas.BatchUploadResponse(
        total_files=len(files),
        successful=successful,
        failed=failed,
        results=results
    )


@router.put("/{resume_id}", response_model=schemas.ResumeResponse)
async def update_resume(
    resume_id: int,
    resume_update: schemas.ResumeUpdate,
    db: Session = Depends(get_db)
):
    """
    Update resume metadata
    """
    db_resume = db.query(models.Resume).filter(
        models.Resume.id == resume_id
    ).first()
    
    if not db_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with id {resume_id} not found"
        )
    
    # Update fields
    update_data = resume_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_resume, field, value)
    
    db.commit()
    db.refresh(db_resume)
    
    logger.info(f"Updated resume: {db_resume.resume_name} (ID: {resume_id})")
    
    return db_resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a resume and its file
    """
    db_resume = db.query(models.Resume).filter(
        models.Resume.id == resume_id
    ).first()
    
    if not db_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with id {resume_id} not found"
        )
    
    # Delete file
    file_path = Path(db_resume.file_path)
    delete_file(file_path)
    
    # Delete from database
    db.delete(db_resume)
    db.commit()
    
    logger.info(f"Deleted resume: {db_resume.resume_name} (ID: {resume_id})")
    
    return None


@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Download a resume file
    """
    from fastapi.responses import FileResponse
    
    db_resume = db.query(models.Resume).filter(
        models.Resume.id == resume_id
    ).first()
    
    if not db_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with id {resume_id} not found"
        )
    
    file_path = Path(db_resume.file_path)
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume file not found on disk"
        )
    
    return FileResponse(
        path=str(file_path),
        media_type='application/octet-stream',
        filename=db_resume.file_name
    )


@router.post("/{resume_id}/reparse", response_model=schemas.ResumeResponse)
async def reparse_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Re-parse a resume file
    """
    db_resume = db.query(models.Resume).filter(
        models.Resume.id == resume_id
    ).first()
    
    if not db_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with id {resume_id} not found"
        )
    
    try:
        # Parse resume again
        file_path = Path(db_resume.file_path)
        parsed_data = ResumeParser.parse_resume(file_path)
        
        # Update resume record
        db_resume.raw_text = parsed_data.get('raw_text')
        db_resume.email = parsed_data.get('email')
        db_resume.phone = parsed_data.get('phone')
        db_resume.total_experience = parsed_data.get('total_experience')
        db_resume.skills = parsed_data.get('skills', [])
        db_resume.programming_languages = parsed_data.get('programming_languages', [])
        db_resume.frameworks = parsed_data.get('frameworks', [])
        db_resume.databases = parsed_data.get('databases', [])
        db_resume.cloud_platforms = parsed_data.get('cloud_platforms', [])
        db_resume.devops_tools = parsed_data.get('devops_tools', [])
        db_resume.ai_ml_skills = parsed_data.get('ai_ml_skills', [])
        db_resume.certifications = parsed_data.get('certifications', [])
        db_resume.companies = parsed_data.get('companies', [])
        
        db.commit()
        db.refresh(db_resume)
        
        logger.info(f"Re-parsed resume: {db_resume.resume_name} (ID: {resume_id})")
        
        return db_resume
        
    except Exception as e:
        logger.error(f"Error re-parsing resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to re-parse resume: {str(e)}"
        )
