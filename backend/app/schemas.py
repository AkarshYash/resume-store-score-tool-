"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# Candidate Schemas
# ============================================================================

class CandidateBase(BaseModel):
    """Base schema for candidate data"""
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    visa_status: Optional[str] = Field(None, max_length=100)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class CandidateCreate(CandidateBase):
    """Schema for creating a new candidate"""
    pass


class CandidateUpdate(BaseModel):
    """Schema for updating a candidate (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    visa_status: Optional[str] = None
    linkedin_url: Optional[str] = None
    notes: Optional[str] = None


class CandidateResponse(CandidateBase):
    """Schema for candidate response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    resume_count: int = 0  # Calculated field
    
    class Config:
        from_attributes = True


class CandidateDetail(CandidateResponse):
    """Detailed candidate with resumes"""
    resumes: List['ResumeResponse'] = []
    
    class Config:
        from_attributes = True


# ============================================================================
# Resume Schemas
# ============================================================================

class ResumeBase(BaseModel):
    """Base schema for resume data"""
    resume_name: str = Field(..., min_length=1, max_length=255)
    specialization: Optional[str] = None


class ResumeCreate(ResumeBase):
    """Schema for creating a new resume"""
    candidate_id: int


class ResumeUpdate(BaseModel):
    """Schema for updating a resume"""
    resume_name: Optional[str] = None
    specialization: Optional[str] = None


class ResumeResponse(BaseModel):
    """Schema for resume response"""
    id: int
    candidate_id: int
    resume_name: str
    file_name: str
    file_type: str
    file_size: int
    
    # Extracted info
    email: Optional[str] = None
    phone: Optional[str] = None
    total_experience: Optional[float] = None
    role_type: Optional[str] = None
    specialization: Optional[str] = None
    
    # Skills
    skills: List[str] = []
    programming_languages: List[str] = []
    frameworks: List[str] = []
    databases: List[str] = []
    cloud_platforms: List[str] = []
    devops_tools: List[str] = []
    ai_ml_skills: List[str] = []
    certifications: List[str] = []
    
    # ATS
    ats_score: Optional[float] = None
    
    # Metadata
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ResumeDetail(ResumeResponse):
    """Detailed resume with all information"""
    raw_text: Optional[str] = None
    companies: List[str] = []
    projects: List[str] = []
    education: List[Dict[str, Any]] = []
    candidate_name: Optional[str] = None  # Joined from candidate
    
    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """Response schema for file upload"""
    success: bool
    message: str
    resume_id: Optional[int] = None
    file_name: Optional[str] = None


class BatchUploadResponse(BaseModel):
    """Response schema for batch file upload"""
    total_files: int
    successful: int
    failed: int
    results: List[FileUploadResponse] = []


class ExtractedFileName(BaseModel):
    """Extracted name from filename"""
    original_filename: str
    suggested_name: str
    full_name_without_ext: str


class ResumeWithCandidate(ResumeResponse):
    """Resume with candidate information"""
    candidate_name: str
    candidate_email: Optional[str] = None


# ============================================================================
# Job Description Schemas
# ============================================================================

class JobDescriptionBase(BaseModel):
    """Base schema for job description"""
    job_title: str = Field(..., min_length=1, max_length=500)
    company_name: Optional[str] = None
    location: Optional[str] = None
    raw_text: str = Field(..., min_length=10)


class JobDescriptionCreate(JobDescriptionBase):
    """Schema for creating a job description"""
    pass


class JobDescriptionCreateFromTitle(BaseModel):
    """Schema for creating JD from just a job title"""
    job_title: str = Field(..., min_length=3, max_length=500)


class JobDescriptionResponse(BaseModel):
    """Schema for job description response"""
    id: int
    job_title: str
    company_name: Optional[str] = None
    location: Optional[str] = None
    raw_text: str
    
    # Requirements
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    years_experience: Optional[float] = None
    
    # Technologies
    programming_languages: List[str] = []
    frameworks: List[str] = []
    databases: List[str] = []
    cloud_platforms: List[str] = []
    devops_tools: List[str] = []
    ai_ml_requirements: List[str] = []
    certifications: List[str] = []
    
    # Other
    education_required: Optional[str] = None
    soft_skills: List[str] = []
    
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Matching Schemas
# ============================================================================

class MatchRequest(BaseModel):
    """Request schema for matching resumes to JD"""
    job_description_id: Optional[int] = None
    job_description_text: Optional[str] = None
    job_title_only: Optional[str] = None
    top_n: int = Field(default=10, ge=1, le=100)
    
    @field_validator('job_description_text')
    def validate_jd_text(cls, v):
        if v is not None and len(v.strip()) < 10:
            raise ValueError('Job description must be at least 10 characters')
        return v


class SkillMatch(BaseModel):
    """Schema for individual skill matching"""
    skill: str
    match_type: str  # "exact", "similar", "missing"
    similarity: float = Field(ge=0.0, le=1.0)


class MatchResult(BaseModel):
    """Schema for matching result"""
    resume_id: int
    candidate_id: int
    candidate_name: str
    resume_name: str
    file_name: str
    
    # Scores
    overall_match_score: float = Field(ge=0.0, le=100.0)
    technical_match_score: Optional[float] = None
    experience_match_score: Optional[float] = None
    cloud_match_score: Optional[float] = None
    programming_match_score: Optional[float] = None
    certification_match_score: Optional[float] = None
    education_match_score: Optional[float] = None
    
    # Skills analysis
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    additional_skills: List[str] = []
    partial_skills: List[Dict[str, Any]] = []
    
    # Ranking
    rank: int
    
    # Explanation
    match_explanation: str
    
    # Recommendations
    improvement_suggestions: List[str] = []
    
    class Config:
        from_attributes = True


class MatchResponse(BaseModel):
    """Response schema for match request"""
    job_description: JobDescriptionResponse
    total_resumes_analyzed: int
    results: List[MatchResult]
    processing_time_seconds: float


# ============================================================================
# Comparison Schemas
# ============================================================================

class ComparisonRequest(BaseModel):
    """Request schema for comparing two resumes"""
    resume_id_1: int
    resume_id_2: int


class ComparisonResult(BaseModel):
    """Schema for resume comparison result"""
    resume_1: ResumeResponse
    resume_2: ResumeResponse
    
    # Common elements
    common_skills: List[str] = []
    common_technologies: List[str] = []
    common_certifications: List[str] = []
    
    # Unique to each
    unique_skills_1: List[str] = []
    unique_skills_2: List[str] = []
    
    # Differences
    experience_difference: Optional[float] = None  # Years
    cloud_platforms_comparison: Dict[str, List[str]] = {}
    programming_languages_comparison: Dict[str, List[str]] = {}
    
    # Summary
    similarity_score: float = Field(ge=0.0, le=100.0)
    recommendation: str


# ============================================================================
# Search Schemas
# ============================================================================

class SearchRequest(BaseModel):
    """Request schema for searching resumes"""
    query: str = Field(..., min_length=1)
    filters: Optional[Dict[str, Any]] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SearchResponse(BaseModel):
    """Response schema for search"""
    total_count: int
    page: int
    page_size: int
    total_pages: int
    results: List[ResumeResponse]


# ============================================================================
# Analytics Schemas
# ============================================================================

class SkillDistribution(BaseModel):
    """Schema for skill distribution"""
    skill: str
    count: int
    percentage: float


class TechnologyStats(BaseModel):
    """Schema for technology statistics"""
    category: str  # "cloud", "programming", "database"
    technologies: List[SkillDistribution]


class DashboardStats(BaseModel):
    """Schema for dashboard statistics"""
    total_candidates: int
    total_resumes: int
    recent_searches: int
    avg_match_score: Optional[float] = None
    
    # Distributions
    top_skills: List[SkillDistribution] = []
    cloud_distribution: List[SkillDistribution] = []
    programming_languages: List[SkillDistribution] = []
    
    # Recent activity
    recent_uploads: List[ResumeResponse] = []


# ============================================================================
# File Upload Schemas
# ============================================================================

class FileUploadResponse(BaseModel):
    """Response schema for file upload"""
    success: bool
    message: str
    resume_id: Optional[int] = None
    file_name: Optional[str] = None


class BatchUploadResponse(BaseModel):
    """Response schema for batch file upload"""
    total_files: int
    successful: int
    failed: int
    results: List[FileUploadResponse]


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str
    detail: Optional[str] = None
    status_code: int


class ValidationError(BaseModel):
    """Schema for validation errors"""
    field: str
    message: str


# Update forward references
CandidateDetail.model_rebuild()
