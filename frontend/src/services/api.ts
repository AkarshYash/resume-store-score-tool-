/**
 * API service for communicating with the backend
 */

import axios, { AxiosError, AxiosInstance } from 'axios';
import type {
    AnalyticsData,
    Candidate,
    DashboardStats,
    MatchRequest,
    MatchResult,
    Resume
} from '../types';

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "https://resume-store-score-tool.onrender.com/api/v1";

console.log("API URL:", API_BASE_URL);

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // ==================== Candidates ====================

  async getCandidates(): Promise<Candidate[]> {
    const response = await this.client.get<Candidate[]>('/candidates/');
    return response.data;
  }

  async getCandidate(id: number): Promise<Candidate> {
    const response = await this.client.get<Candidate>(`/candidates/${id}`);
    return response.data;
  }

  async createCandidate(data: Partial<Candidate>): Promise<Candidate> {
    const response = await this.client.post<Candidate>('/candidates/', data);
    return response.data;
  }

  async updateCandidate(id: number, data: Partial<Candidate>): Promise<Candidate> {
    const response = await this.client.put<Candidate>(`/candidates/${id}`, data);
    return response.data;
  }

  async deleteCandidate(id: number): Promise<void> {
    await this.client.delete(`/candidates/${id}`);
  }

  // ==================== Resumes ====================

  async getResumes(candidateId?: number): Promise<Resume[]> {
    const params = candidateId ? { candidate_id: candidateId } : {};
    const response = await this.client.get<Resume[]>('/resumes/', { params });
    return response.data;
  }

  async getResume(id: number): Promise<Resume> {
    const response = await this.client.get<Resume>(`/resumes/${id}`);
    return response.data;
  }

  async uploadResume(candidateId: number, file: File, resumeName: string): Promise<Resume> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('candidate_id', candidateId.toString());
    formData.append('resume_name', resumeName);

    const response = await this.client.post<Resume>('/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async deleteResume(id: number): Promise<void> {
    await this.client.delete(`/resumes/${id}`);
  }

  async downloadResume(id: number): Promise<Blob> {
    const response = await this.client.get(`/resumes/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  }

  // ==================== Job Matching ====================

  async matchResumes(request: MatchRequest): Promise<MatchResult[]> {
    let endpoint = '/matching/match';
    let data: any = {};

    if (request.job_file) {
      // Upload job description file
      const formData = new FormData();
      formData.append('file', request.job_file);
      endpoint = '/matching/match-file';
      data = formData;
    } else if (request.job_title) {
      // Match by job title
      endpoint = '/matching/match-title';
      data = { job_title: request.job_title };
    } else if (request.job_description) {
      // Match by text
      data = { job_description: request.job_description };
    }

    const response = await this.client.post<MatchResult[]>(endpoint, data, {
      headers: request.job_file
        ? { 'Content-Type': 'multipart/form-data' }
        : { 'Content-Type': 'application/json' },
    });

    return response.data;
  }

  async compareResumes(resumeIds: number[]): Promise<any> {
    const response = await this.client.post('/matching/compare', {
      resume_ids: resumeIds,
    });
    return response.data;
  }

  // ==================== Search ====================

  async searchResumes(params: {
    query?: string;
    skills?: string[];
    cloud_platforms?: string[];
    programming_languages?: string[];
    min_experience?: number;
    max_experience?: number;
  }): Promise<Resume[]> {
    const response = await this.client.get<Resume[]>('/search/resumes', { params });
    return response.data;
  }

  async searchCandidates(query: string): Promise<Candidate[]> {
    const response = await this.client.get<Candidate[]>('/search/candidates', {
      params: { q: query },
    });
    return response.data;
  }

  // ==================== Analytics ====================

  async getAnalytics(): Promise<AnalyticsData> {
    const response = await this.client.get<AnalyticsData>('/analytics/');
    return response.data;
  }

  async getDashboardStats(): Promise<DashboardStats> {
    const response = await this.client.get<DashboardStats>('/analytics/dashboard');
    return response.data;
  }

  async getSkillsDistribution(): Promise<any> {
    const response = await this.client.get('/analytics/skills-distribution');
    return response.data;
  }

  async getTechnologyTrends(): Promise<any> {
    const response = await this.client.get('/analytics/technology-trends');
    return response.data;
  }

  // ==================== Health Check ====================

  async healthCheck(): Promise<{ status: string; timestamp: number }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const api = new ApiService();
export default api;
