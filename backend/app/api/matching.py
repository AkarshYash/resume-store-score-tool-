"""
API endpoints for AI-powered resume matching
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import time
import logging
from pathlib import Path

from app.database import get_db
from app import models, schemas
from app.services.ai_matcher import AIMatcher
from app.services.resume_parser import ResumeParser

router = APIRouter()
logger = logging.getLogger(__name__)


def parse_job_description_text(jd_text: str) -> dict:
    """
    Parse job description text to extract requirements
    (Simplified version - can be enhanced with NLP)
    """
    # Use the same skill extraction as resume parser
    skills_data = ResumeParser.extract_all_skills(jd_text)
    
    # Extract experience
    experience = ResumeParser.extract_experience_years(jd_text)
    
    # Extract certifications
    certifications = ResumeParser.extract_certifications(jd_text)
    
    # Try to identify required vs preferred skills
    # Simple heuristic: skills mentioned with "required", "must have" are required
    jd_lower = jd_text.lower()
    all_skills = []
    for skill_list in skills_data.values():
        all_skills.extend(skill_list)
    
    required_skills = []
    preferred_skills = []
    
    for skill in all_skills:
        # Check if skill is mentioned near "required" or "must"
        skill_lower = skill.lower()
        if any(keyword in jd_lower for keyword in [f"required: {skill_lower}", f"must have {skill_lower}", f"mandatory: {skill_lower}"]):
            required_skills.append(skill)
        else:
            preferred_skills.append(skill)
    
    # If no explicit required/preferred split, put all in required
    if not required_skills:
        required_skills = all_skills
        preferred_skills = []
    
    return {
        'required_skills': list(set(required_skills)),
        'preferred_skills': list(set(preferred_skills)),
        'years_experience': experience,
        'programming_languages': skills_data['programming_languages'],
        'frameworks': skills_data['frameworks'],
        'databases': skills_data['databases'],
        'cloud_platforms': skills_data['cloud_platforms'] + skills_data['cloud_services'],
        'devops_tools': skills_data['devops_tools'],
        'ai_ml_requirements': skills_data['ai_ml'],
        'certifications': certifications,
    }


@router.post("/match", response_model=schemas.MatchResponse)
async def match_resumes(
    match_request: schemas.MatchRequest,
    db: Session = Depends(get_db)
):
    """
    Match all resumes against a job description
    Returns ranked list of best matching resumes
    """
    start_time = time.time()
    
    # Get or create job description
    if match_request.job_description_id:
        # Use existing JD
        job_desc = db.query(models.JobDescription).filter(
            models.JobDescription.id == match_request.job_description_id
        ).first()
        
        if not job_desc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job description with id {match_request.job_description_id} not found"
            )
            
    elif match_request.job_description_text:
        # Parse and create new JD
        jd_text = match_request.job_description_text
        parsed_jd = parse_job_description_text(jd_text)
        
        # Try to extract job title from first line or use default
        lines = jd_text.strip().split('\n')
        job_title = lines[0][:500] if lines else "Untitled Position"
        
        job_desc = models.JobDescription(
            job_title=job_title,
            raw_text=jd_text,
            **parsed_jd
        )
        db.add(job_desc)
        db.commit()
        db.refresh(job_desc)
        
    elif match_request.job_title_only:
        # Generate simple JD from job title
        job_title = match_request.job_title_only
        jd_text = f"{job_title}\n\nLooking for candidates with experience in {job_title} role."
        
        job_desc = models.JobDescription(
            job_title=job_title,
            raw_text=jd_text,
            required_skills=[],
            preferred_skills=[]
        )
        db.add(job_desc)
        db.commit()
        db.refresh(job_desc)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide job_description_id, job_description_text, or job_title_only"
        )
    
    # Get all resumes
    all_resumes = db.query(models.Resume).all()
    
    if not all_resumes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resumes found in database. Please upload resumes first."
        )
    
    logger.info(f"Matching {len(all_resumes)} resumes against job: {job_desc.job_title}")
    
    # Initialize matcher
    matcher = AIMatcher()
    
    # Match each resume
    match_results = []
    
    for resume in all_resumes:
        try:
            # Prepare resume data
            resume_data = {
                'id': resume.id,
                'raw_text': resume.raw_text or "",
                'skills': resume.skills or [],
                'programming_languages': resume.programming_languages or [],
                'frameworks': resume.frameworks or [],
                'databases': resume.databases or [],
                'cloud_platforms': resume.cloud_platforms or [],
                'devops_tools': resume.devops_tools or [],
                'ai_ml_skills': resume.ai_ml_skills or [],
                'certifications': resume.certifications or [],
                'total_experience': resume.total_experience,
            }
            
            # Prepare job data
            job_data = {
                'job_title': job_desc.job_title,
                'raw_text': job_desc.raw_text,
                'required_skills': job_desc.required_skills or [],
                'preferred_skills': job_desc.preferred_skills or [],
                'programming_languages': job_desc.programming_languages or [],
                'frameworks': job_desc.frameworks or [],
                'databases': job_desc.databases or [],
                'cloud_platforms': job_desc.cloud_platforms or [],
                'devops_tools': job_desc.devops_tools or [],
                'ai_ml_requirements': job_desc.ai_ml_requirements or [],
                'certifications': job_desc.certifications or [],
                'years_experience': job_desc.years_experience,
            }
            
            # Perform matching
            match_result = matcher.match_resume_to_job(resume_data, job_data)
            
            # Create search result record
            search_result = models.SearchResult(
                job_description_id=job_desc.id,
                resume_id=resume.id,
                overall_match_score=match_result['overall_match_score'],
                technical_match_score=match_result['technical_match_score'],
                experience_match_score=match_result['experience_match_score'],
                cloud_match_score=match_result['cloud_match_score'],
                programming_match_score=match_result['programming_match_score'],
                certification_match_score=match_result['certification_match_score'],
                matched_skills=match_result['matched_skills'],
                missing_skills=match_result['missing_skills'],
                additional_skills=match_result['additional_skills'],
                partial_skills=match_result['partial_skills'],
                match_explanation=match_result['match_explanation'],
                improvement_suggestions=match_result['improvement_suggestions']
            )
            
            db.add(search_result)
            
            # Add to results
            match_results.append({
                'resume': resume,
                'match_data': match_result
            })
            
        except Exception as e:
            logger.error(f"Error matching resume {resume.id}: {e}")
            continue
    
    # Commit all search results
    db.commit()
    
    # Sort by overall score (descending)
    match_results.sort(key=lambda x: x['match_data']['overall_match_score'], reverse=True)
    
    # Limit to top N
    match_results = match_results[:match_request.top_n]
    
    # Update rankings
    for rank, result in enumerate(match_results, start=1):
        search_result = db.query(models.SearchResult).filter(
            models.SearchResult.job_description_id == job_desc.id,
            models.SearchResult.resume_id == result['resume'].id
        ).first()
        if search_result:
            search_result.rank = rank
    
    db.commit()
    
    # Build response
    results = []
    for rank, result in enumerate(match_results, start=1):
        resume = result['resume']
        match_data = result['match_data']
        
        results.append(schemas.MatchResult(
            resume_id=resume.id,
            candidate_id=resume.candidate_id,
            candidate_name=resume.candidate.name,
            resume_name=resume.resume_name,
            file_name=resume.file_name,
            rank=rank,
            **match_data
        ))
    
    processing_time = time.time() - start_time
    
    logger.info(f"Matching completed in {processing_time:.2f}s. Top match: {results[0].resume_name if results else 'None'} ({results[0].overall_match_score:.1f}%)")
    
    return schemas.MatchResponse(
        job_description=schemas.JobDescriptionResponse.model_validate(job_desc),
        total_resumes_analyzed=len(all_resumes),
        results=results,
        processing_time_seconds=round(processing_time, 2)
    )


@router.post("/match-upload", response_model=schemas.MatchResponse)
async def match_resumes_from_upload(
    file: UploadFile = File(...),
    top_n: int = Form(10),
    db: Session = Depends(get_db)
):
    """
    Upload a job description file and match resumes
    """
    try:
        # Save file temporarily
        temp_path = Path("temp_jd" + Path(file.filename).suffix)
        
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract text
        jd_text = ResumeParser.extract_text(temp_path)
        
        # Delete temp file
        temp_path.unlink()
        
        # Create match request
        match_request = schemas.MatchRequest(
            job_description_text=jd_text,
            top_n=top_n
        )
        
        # Use the match endpoint
        return await match_resumes(match_request, db)
        
    except Exception as e:
        logger.error(f"Error processing uploaded JD: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process job description: {str(e)}"
        )


@router.post("/compare", response_model=schemas.ComparisonResult)
async def compare_resumes(
    comparison: schemas.ComparisonRequest,
    db: Session = Depends(get_db)
):
    """
    Compare two resumes side-by-side
    """
    # Get both resumes
    resume1 = db.query(models.Resume).filter(
        models.Resume.id == comparison.resume_id_1
    ).first()
    
    resume2 = db.query(models.Resume).filter(
        models.Resume.id == comparison.resume_id_2
    ).first()
    
    if not resume1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with id {comparison.resume_id_1} not found"
        )
    
    if not resume2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with id {comparison.resume_id_2} not found"
        )
    
    # Find common and unique elements
    skills1 = set(resume1.skills or [])
    skills2 = set(resume2.skills or [])
    
    common_skills = list(skills1 & skills2)
    unique_skills_1 = list(skills1 - skills2)
    unique_skills_2 = list(skills2 - skills1)
    
    # Cloud platforms
    cloud1 = set(resume1.cloud_platforms or [])
    cloud2 = set(resume2.cloud_platforms or [])
    
    cloud_comparison = {
        "common": list(cloud1 & cloud2),
        "resume_1_only": list(cloud1 - cloud2),
        "resume_2_only": list(cloud2 - cloud1)
    }
    
    # Programming languages
    prog1 = set(resume1.programming_languages or [])
    prog2 = set(resume2.programming_languages or [])
    
    prog_comparison = {
        "common": list(prog1 & prog2),
        "resume_1_only": list(prog1 - prog2),
        "resume_2_only": list(prog2 - prog1)
    }
    
    # Calculate similarity
    all_skills = skills1 | skills2
    if all_skills:
        similarity = (len(common_skills) / len(all_skills)) * 100
    else:
        similarity = 0.0
    
    # Experience difference
    exp_diff = None
    if resume1.total_experience and resume2.total_experience:
        exp_diff = resume1.total_experience - resume2.total_experience
    
    # Recommendation
    if similarity >= 80:
        recommendation = "Very similar resumes. Choose based on specific role requirements."
    elif similarity >= 60:
        recommendation = "Moderately similar. Review unique skills for role fit."
    else:
        recommendation = "Significantly different skill sets. Choose based on job requirements."
    
    return schemas.ComparisonResult(
        resume_1=schemas.ResumeResponse.model_validate(resume1),
        resume_2=schemas.ResumeResponse.model_validate(resume2),
        common_skills=common_skills,
        unique_skills_1=unique_skills_1,
        unique_skills_2=unique_skills_2,
        experience_difference=exp_diff,
        cloud_platforms_comparison=cloud_comparison,
        programming_languages_comparison=prog_comparison,
        similarity_score=round(similarity, 2),
        recommendation=recommendation
    )
