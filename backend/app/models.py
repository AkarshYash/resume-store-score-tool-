"""
SQLAlchemy database models for the Resume Intelligence Platform
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Candidate(Base):
    """
    Candidate model - represents a person who has multiple resumes
    """
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    visa_status = Column(String(100), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship: One candidate has many resumes
    resumes = relationship("Resume", back_populates="candidate", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Candidate(id={self.id}, name='{self.name}')>"


class Resume(Base):
    """
    Resume model - represents a single resume file for a candidate
    Each candidate can have multiple specialized resumes (Python, AWS, Azure, etc.)
    """
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    
    # File information
    resume_name = Column(String(255), nullable=False, index=True)  # e.g., "Python_GenAI"
    file_name = Column(String(500), nullable=False)  # e.g., "Nirav_Python_GenAI.docx"
    file_path = Column(String(1000), nullable=False)  # Relative path to uploaded file
    file_type = Column(String(10), nullable=False)  # pdf, docx
    file_size = Column(Integer, nullable=False)  # in bytes
    
    # Parsed content
    raw_text = Column(Text, nullable=True)
    
    # Extracted information
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    total_experience = Column(Float, nullable=True)  # Years
    
    # Skills and technologies (stored as JSON arrays)
    skills = Column(JSON, nullable=True)  # ["Python", "FastAPI", "AWS"]
    programming_languages = Column(JSON, nullable=True)  # ["Python", "JavaScript"]
    frameworks = Column(JSON, nullable=True)  # ["React", "Django", "FastAPI"]
    databases = Column(JSON, nullable=True)  # ["PostgreSQL", "MongoDB"]
    cloud_platforms = Column(JSON, nullable=True)  # ["AWS", "Azure", "GCP"]
    devops_tools = Column(JSON, nullable=True)  # ["Docker", "Kubernetes", "Terraform"]
    ai_ml_skills = Column(JSON, nullable=True)  # ["TensorFlow", "PyTorch", "LangChain"]
    certifications = Column(JSON, nullable=True)  # ["AWS Certified", "Azure"]
    
    # Work history
    companies = Column(JSON, nullable=True)  # ["Google", "Microsoft"]
    projects = Column(JSON, nullable=True)  # List of project titles
    
    # Education
    education = Column(JSON, nullable=True)  # [{"degree": "BS CS", "school": "MIT"}]
    
    # Role and specialization
    role_type = Column(String(255), nullable=True, index=True)  # "GenAI Engineer"
    specialization = Column(String(255), nullable=True)  # "Python", "AWS", "Data"
    
    # ATS scores
    ats_score = Column(Float, nullable=True)  # 0-100
    keyword_density = Column(Float, nullable=True)
    
    # Embeddings (stored separately for performance)
    embedding_path = Column(String(1000), nullable=True)  # Path to embedding file
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship: Many resumes belong to one candidate
    candidate = relationship("Candidate", back_populates="resumes")
    
    # Relationship: One resume has many search results
    search_results = relationship("SearchResult", back_populates="resume", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Resume(id={self.id}, name='{self.resume_name}', candidate='{self.candidate.name if self.candidate else None}')>"


class JobDescription(Base):
    """
    Job Description model - stores parsed job descriptions
    """
    __tablename__ = "job_descriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Job information
    job_title = Column(String(500), nullable=False, index=True)
    company_name = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    
    # Original JD
    raw_text = Column(Text, nullable=False)
    
    # Parsed requirements
    required_skills = Column(JSON, nullable=True)  # Must-have skills
    preferred_skills = Column(JSON, nullable=True)  # Nice-to-have skills
    years_experience = Column(Float, nullable=True)
    
    # Technologies
    programming_languages = Column(JSON, nullable=True)
    frameworks = Column(JSON, nullable=True)
    databases = Column(JSON, nullable=True)
    cloud_platforms = Column(JSON, nullable=True)
    devops_tools = Column(JSON, nullable=True)
    ai_ml_requirements = Column(JSON, nullable=True)
    
    # Other requirements
    certifications = Column(JSON, nullable=True)
    education_required = Column(String(255), nullable=True)
    soft_skills = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship: One JD has many search results
    search_results = relationship("SearchResult", back_populates="job_description", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<JobDescription(id={self.id}, title='{self.job_title}')>"


class SearchResult(Base):
    """
    Search Result model - stores matching results between JDs and resumes
    """
    __tablename__ = "search_results"
    
    id = Column(Integer, primary_key=True, index=True)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    # Overall scores
    overall_match_score = Column(Float, nullable=False)  # 0-100
    technical_match_score = Column(Float, nullable=True)
    experience_match_score = Column(Float, nullable=True)
    cloud_match_score = Column(Float, nullable=True)
    programming_match_score = Column(Float, nullable=True)
    certification_match_score = Column(Float, nullable=True)
    education_match_score = Column(Float, nullable=True)
    
    # Detailed matching
    matched_skills = Column(JSON, nullable=True)  # Skills that match
    missing_skills = Column(JSON, nullable=True)  # Required but not in resume
    additional_skills = Column(JSON, nullable=True)  # In resume but not in JD
    partial_skills = Column(JSON, nullable=True)  # Similar but not exact match
    
    # Ranking
    rank = Column(Integer, nullable=True)
    
    # Explanation
    match_explanation = Column(Text, nullable=True)
    
    # Recommendations
    improvement_suggestions = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    job_description = relationship("JobDescription", back_populates="search_results")
    resume = relationship("Resume", back_populates="search_results")
    
    def __repr__(self):
        return f"<SearchResult(id={self.id}, score={self.overall_match_score})>"


class Analytics(Base):
    """
    Analytics model - stores aggregated analytics data
    """
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Metrics
    metric_type = Column(String(100), nullable=False, index=True)  # "skill_count", "search_count"
    metric_key = Column(String(255), nullable=False)  # "Python", "AWS"
    metric_value = Column(Float, nullable=False)
    
    # Metadata
    date = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Analytics(type='{self.metric_type}', key='{self.metric_key}', value={self.metric_value})>"
