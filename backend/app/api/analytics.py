"""
API endpoints for analytics and dashboard statistics
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from collections import Counter
import logging

from app.database import get_db
from app import models, schemas

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/dashboard", response_model=schemas.DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db)
):
    """
    Get statistics for dashboard
    """
    # Basic counts
    total_candidates = db.query(func.count(models.Candidate.id)).scalar()
    total_resumes = db.query(func.count(models.Resume.id)).scalar()
    
    # Recent searches (last 30 days or all searches)
    recent_searches = db.query(func.count(models.SearchResult.id)).scalar()
    
    # Average match score
    avg_match_score = db.query(func.avg(models.SearchResult.overall_match_score)).scalar()
    
    # Get all resumes for skill analysis
    resumes = db.query(models.Resume).all()
    
    # Count skills
    skill_counter = Counter()
    cloud_counter = Counter()
    lang_counter = Counter()
    
    for resume in resumes:
        if resume.skills:
            skill_counter.update(resume.skills)
        if resume.cloud_platforms:
            cloud_counter.update(resume.cloud_platforms)
        if resume.programming_languages:
            lang_counter.update(resume.programming_languages)
    
    # Top skills
    top_skills = [
        schemas.SkillDistribution(
            skill=skill,
            count=count,
            percentage=round((count / total_resumes * 100) if total_resumes > 0 else 0, 2)
        )
        for skill, count in skill_counter.most_common(10)
    ]
    
    # Cloud distribution
    cloud_distribution = [
        schemas.SkillDistribution(
            skill=cloud,
            count=count,
            percentage=round((count / total_resumes * 100) if total_resumes > 0 else 0, 2)
        )
        for cloud, count in cloud_counter.most_common(10)
    ]
    
    # Programming languages
    programming_languages = [
        schemas.SkillDistribution(
            skill=lang,
            count=count,
            percentage=round((count / total_resumes * 100) if total_resumes > 0 else 0, 2)
        )
        for lang, count in lang_counter.most_common(10)
    ]
    
    # Recent uploads
    recent_uploads = db.query(models.Resume).order_by(
        models.Resume.created_at.desc()
    ).limit(5).all()
    
    return schemas.DashboardStats(
        total_candidates=total_candidates or 0,
        total_resumes=total_resumes or 0,
        recent_searches=recent_searches or 0,
        avg_match_score=round(avg_match_score, 2) if avg_match_score else None,
        top_skills=top_skills,
        cloud_distribution=cloud_distribution,
        programming_languages=programming_languages,
        recent_uploads=[schemas.ResumeResponse.model_validate(r) for r in recent_uploads]
    )


@router.get("/skills/distribution", response_model=List[schemas.SkillDistribution])
async def get_skill_distribution(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get distribution of all skills across resumes
    """
    resumes = db.query(models.Resume).all()
    total_resumes = len(resumes)
    
    skill_counter = Counter()
    for resume in resumes:
        if resume.skills:
            skill_counter.update(resume.skills)
    
    return [
        schemas.SkillDistribution(
            skill=skill,
            count=count,
            percentage=round((count / total_resumes * 100) if total_resumes > 0 else 0, 2)
        )
        for skill, count in skill_counter.most_common(limit)
    ]


@router.get("/technologies", response_model=List[schemas.TechnologyStats])
async def get_technology_stats(
    db: Session = Depends(get_db)
):
    """
    Get technology statistics by category
    """
    resumes = db.query(models.Resume).all()
    total_resumes = len(resumes)
    
    # Count by category
    cloud_counter = Counter()
    lang_counter = Counter()
    db_counter = Counter()
    framework_counter = Counter()
    devops_counter = Counter()
    ai_counter = Counter()
    
    for resume in resumes:
        if resume.cloud_platforms:
            cloud_counter.update(resume.cloud_platforms)
        if resume.programming_languages:
            lang_counter.update(resume.programming_languages)
        if resume.databases:
            db_counter.update(resume.databases)
        if resume.frameworks:
            framework_counter.update(resume.frameworks)
        if resume.devops_tools:
            devops_counter.update(resume.devops_tools)
        if resume.ai_ml_skills:
            ai_counter.update(resume.ai_ml_skills)
    
    def create_distribution(counter: Counter) -> List[schemas.SkillDistribution]:
        return [
            schemas.SkillDistribution(
                skill=item,
                count=count,
                percentage=round((count / total_resumes * 100) if total_resumes > 0 else 0, 2)
            )
            for item, count in counter.most_common(10)
        ]
    
    return [
        schemas.TechnologyStats(
            category="Cloud Platforms",
            technologies=create_distribution(cloud_counter)
        ),
        schemas.TechnologyStats(
            category="Programming Languages",
            technologies=create_distribution(lang_counter)
        ),
        schemas.TechnologyStats(
            category="Databases",
            technologies=create_distribution(db_counter)
        ),
        schemas.TechnologyStats(
            category="Frameworks",
            technologies=create_distribution(framework_counter)
        ),
        schemas.TechnologyStats(
            category="DevOps Tools",
            technologies=create_distribution(devops_counter)
        ),
        schemas.TechnologyStats(
            category="AI/ML",
            technologies=create_distribution(ai_counter)
        ),
    ]


@router.get("/match-history", response_model=List[dict])
async def get_match_history(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent match history
    """
    recent_matches = db.query(models.SearchResult).join(
        models.JobDescription
    ).join(
        models.Resume
    ).order_by(
        models.SearchResult.created_at.desc()
    ).limit(limit).all()
    
    results = []
    for match in recent_matches:
        results.append({
            'id': match.id,
            'job_title': match.job_description.job_title,
            'resume_name': match.resume.resume_name,
            'candidate_name': match.resume.candidate.name,
            'match_score': match.overall_match_score,
            'rank': match.rank,
            'created_at': match.created_at.isoformat()
        })
    
    return results
