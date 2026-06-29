from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
from collections import Counter
from datetime import datetime, timedelta

from app.database import get_db
from app import models
from app.services.resume_parser import ResumeParser

router = APIRouter()
logger = logging.getLogger(__name__)

class JDAnalyzeRequest(BaseModel):
    job_title: Optional[str] = None
    raw_text: str

class JDAnalyzeResponse(BaseModel):
    id: int
    job_title: str
    role_type: str
    technologies_found: List[str]
    technology_categories: Dict[str, List[str]]
    years_experience: Optional[float] = None
    message: str

class JDTrend(BaseModel):
    technology: str
    count: int
    category: str


def _display_skill(skill: str) -> str:
    special = {
        "aws": "AWS",
        "gcp": "GCP",
        "sql": "SQL",
        "nlp": "NLP",
        "llm": "LLM",
        "rag": "RAG",
        "faiss": "FAISS",
        "api": "API",
        "openai": "OpenAI",
        "node.js": "Node.js",
        "nodejs": "Node.js",
        "scikit-learn": "Scikit-learn",
    }
    return special.get(skill.lower(), skill.title())


def _infer_role(job_title: Optional[str], raw_text: str) -> str:
    text = f"{job_title or ''} {raw_text[:1000]}".lower()
    role_patterns = [
        ("GenAI Engineer", ["genai", "generative ai", "rag", "llm", "langchain"]),
        ("Data Engineer", ["data engineer", "etl", "databricks", "spark", "airflow"]),
        ("Cloud Engineer", ["cloud engineer", "aws", "azure", "gcp", "terraform"]),
        ("DevOps Engineer", ["devops", "kubernetes", "docker", "jenkins"]),
        ("Full Stack Developer", ["full stack", "fullstack", "react", "node.js"]),
        ("Backend Engineer", ["backend", "fastapi", "django", "spring"]),
        ("Frontend Developer", ["frontend", "react", "angular", "vue"]),
        ("Security Engineer", ["security", "cyber", "iam", "soc"]),
    ]
    for role, keywords in role_patterns:
        if any(keyword in text for keyword in keywords):
            return role
    return (job_title or "General Technology Role").strip()

@router.post("/analyze", response_model=JDAnalyzeResponse)
async def analyze_jd(
    request: JDAnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze a pasted Job Description and extract tech stack
    """
    job_title = (request.job_title or "").strip()
    if not job_title:
        first_line = next((line.strip() for line in request.raw_text.splitlines() if line.strip()), "")
        job_title = first_line[:120] or "Untitled Job Description"

    parsed = ResumeParser.extract_all_skills(request.raw_text)
    categories = {
        "cloud_platforms": parsed["cloud_platforms"] + parsed["cloud_services"],
        "programming_languages": parsed["programming_languages"],
        "frameworks": parsed["frameworks"],
        "databases": parsed["databases"],
        "devops_tools": parsed["devops_tools"],
        "ai_ml_requirements": parsed["ai_ml"] + parsed["data_tools"],
    }
    extracted = {
        key: sorted({_display_skill(item) for item in values})
        for key, values in categories.items()
    }
    all_tech = sorted({item for values in extracted.values() for item in values})
    years_experience = ResumeParser.extract_experience_years(request.raw_text)
    role_type = _infer_role(job_title, request.raw_text)
    
    # Create JobDescription record
    db_jd = models.JobDescription(
        job_title=job_title,
        raw_text=request.raw_text,
        required_skills=all_tech,
        years_experience=years_experience,
        cloud_platforms=extracted['cloud_platforms'],
        programming_languages=extracted['programming_languages'],
        frameworks=extracted['frameworks'],
        databases=extracted['databases'],
        devops_tools=extracted['devops_tools'],
        ai_ml_requirements=extracted['ai_ml_requirements']
    )
    
    db.add(db_jd)
    db.commit()
    db.refresh(db_jd)
    
    return JDAnalyzeResponse(
        id=db_jd.id,
        job_title=db_jd.job_title,
        role_type=role_type,
        technologies_found=all_tech,
        technology_categories=extracted,
        years_experience=years_experience,
        message="Job Description analyzed successfully"
    )

@router.get("/trends", response_model=List[JDTrend])
async def get_jd_trends(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get trending tech stack from JDs analyzed in the last N days
    """
    since = datetime.utcnow() - timedelta(days=days)
    jds = db.query(models.JobDescription).filter(models.JobDescription.created_at >= since).all()

    counter = Counter()
    category_lookup = {}
    for jd in jds:
        tech_lists = {
            "Cloud": jd.cloud_platforms,
            "Programming": jd.programming_languages,
            "Framework": jd.frameworks,
            "Database": jd.databases,
            "DevOps": jd.devops_tools,
            "AI/Data": jd.ai_ml_requirements,
        }

        for category, tech_list in tech_lists.items():
            if tech_list:
                counter.update(tech_list)
                for tech in tech_list:
                    category_lookup.setdefault(tech, category)
                
    trends = []
    for tech, count in counter.most_common(15):
        trends.append(JDTrend(technology=tech, count=count, category=category_lookup.get(tech, "Other")))
        
    return trends
