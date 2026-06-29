/**
 * TypeScript type definitions for the Resume Intelligence Platform
 */

export interface Candidate {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  location?: string;
  visa_status?: string;
  linkedin_url?: string;
  notes?: string;
  created_at: string;
  updated_at?: string;
  resumes?: Resume[];
}

export interface Resume {
  id: number;
  candidate_id: number;
  resume_name: string;
  file_name: string;
  file_path: string;
  file_type: string;
  file_size: number;
  raw_text?: string;
  email?: string;
  phone?: string;
  total_experience?: number;
  skills?: string[];
  programming_languages?: string[];
  frameworks?: string[];
  databases?: string[];
  cloud_platforms?: string[];
  devops_tools?: string[];
  ai_ml_skills?: string[];
  certifications?: string[];
  companies?: string[];
  projects?: string[];
  education?: Education[];
  role_type?: string;
  specialization?: string;
  ats_score?: number;
  keyword_density?: number;
  created_at: string;
  updated_at?: string;
  candidate?: Candidate;
}

export interface Education {
  degree: string;
  school: string;
  year?: string;
  major?: string;
}

export interface JobDescription {
  id: number;
  job_title: string;
  company_name?: string;
  location?: string;
  raw_text: string;
  required_skills?: string[];
  preferred_skills?: string[];
  years_experience?: number;
  programming_languages?: string[];
  frameworks?: string[];
  databases?: string[];
  cloud_platforms?: string[];
  devops_tools?: string[];
  ai_ml_requirements?: string[];
  certifications?: string[];
  education_required?: string;
  soft_skills?: string[];
  created_at: string;
}

export interface MatchResult {
  resume: Resume;
  candidate: Candidate;
  overall_match_score: number;
  technical_match_score: number;
  experience_match_score: number;
  cloud_match_score: number;
  programming_match_score: number;
  certification_match_score: number;
  semantic_similarity: number;
  matched_skills: string[];
  missing_skills: string[];
  additional_skills: string[];
  partial_skills: PartialSkill[];
  match_explanation: string;
  improvement_suggestions: string[];
  rank?: number;
}

export interface PartialSkill {
  skill: string;
  match: string;
  score: number;
}

export interface SearchResult {
  id: number;
  job_description_id: number;
  resume_id: number;
  overall_match_score: number;
  technical_match_score?: number;
  experience_match_score?: number;
  cloud_match_score?: number;
  programming_match_score?: number;
  certification_match_score?: number;
  education_match_score?: number;
  matched_skills?: string[];
  missing_skills?: string[];
  additional_skills?: string[];
  partial_skills?: PartialSkill[];
  rank?: number;
  match_explanation?: string;
  improvement_suggestions?: string[];
  created_at: string;
  job_description?: JobDescription;
  resume?: Resume;
}

export interface AnalyticsData {
  total_candidates: number;
  total_resumes: number;
  recent_searches: number;
  most_used_skills: SkillCount[];
  technology_distribution: TechDistribution;
  cloud_platform_stats: PlatformStats[];
  programming_language_stats: LanguageStats[];
  average_match_scores: AverageScores;
  recent_uploads: Resume[];
}

export interface SkillCount {
  skill: string;
  count: number;
}

export interface TechDistribution {
  programming_languages: number;
  cloud_platforms: number;
  frameworks: number;
  databases: number;
  devops_tools: number;
  ai_ml: number;
}

export interface PlatformStats {
  platform: string;
  count: number;
  percentage: number;
}

export interface LanguageStats {
  language: string;
  count: number;
  percentage: number;
}

export interface AverageScores {
  overall: number;
  technical: number;
  experience: number;
  certifications: number;
}

export interface DashboardStats {
  totalCandidates: number;
  totalResumes: number;
  recentSearches: number;
  mostUsedSkills: SkillCount[];
  recentlyUploaded: Resume[];
}

export interface MatchRequest {
  job_description?: string;
  job_title?: string;
  job_file?: File;
  filters?: MatchFilters;
}

export interface MatchFilters {
  min_experience?: number;
  required_skills?: string[];
  cloud_platforms?: string[];
  programming_languages?: string[];
  location?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
