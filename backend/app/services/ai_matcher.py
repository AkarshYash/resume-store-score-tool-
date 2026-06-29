"""
AI-powered matching engine using Sentence Transformers and similarity algorithms
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import pickle

# Optional imports
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logging.warning("NumPy not installed. AI matching will be limited.")

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    logging.warning("Sentence Transformers not installed. AI matching will be limited.")

try:
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.feature_extraction.text import TfidfVectorizer
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logging.warning("scikit-learn not installed. Some matching features will be limited.")

try:
    from rapidfuzz import fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False
    logging.warning("RapidFuzz not installed. Fuzzy matching will be limited.")

from app.config import settings

logger = logging.getLogger(__name__)

# Global model instances (loaded once)
_sentence_model: Optional[Any] = None
_tfidf_vectorizer: Optional[Any] = None


async def initialize_models():
    """
    Initialize AI models (download if needed)
    """
    global _sentence_model
    
    if not HAS_SENTENCE_TRANSFORMERS:
        logger.warning("Sentence Transformers not available. Install with: pip install sentence-transformers")
        return
    
    if _sentence_model is None:
        logger.info(f"Loading Sentence Transformer model: {settings.SENTENCE_TRANSFORMER_MODEL}")
        _sentence_model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
        logger.info("Sentence Transformer model loaded successfully")


def get_sentence_model():
    """
    Get the sentence transformer model (lazy loading)
    """
    global _sentence_model
    
    if not HAS_SENTENCE_TRANSFORMERS:
        raise ImportError("Sentence Transformers not installed. Install with: pip install sentence-transformers")
    
    if _sentence_model is None:
        logger.info(f"Loading Sentence Transformer model: {settings.SENTENCE_TRANSFORMER_MODEL}")
        _sentence_model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
    
    return _sentence_model


class AIMatcher:
    """
    AI-powered resume matching engine
    """
    
    def __init__(self):
        if HAS_SENTENCE_TRANSFORMERS:
            self.model = get_sentence_model()
        else:
            self.model = None
            logger.warning("AI Matcher initialized without Sentence Transformers. Some features will be limited.")
        self.embedding_cache: Dict[int, Any] = {}
    
    def generate_embedding(self, text: str):
        """
        Generate embedding for text using Sentence Transformers
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector or None if not available
        """
        if not HAS_SENTENCE_TRANSFORMERS or not HAS_NUMPY:
            logger.warning("Sentence Transformers not available for embedding generation")
            return None
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def save_embedding(self, resume_id: int, embedding) -> Optional[Path]:
        """
        Save embedding to disk for caching
        
        Args:
            resume_id: Resume ID
            embedding: Embedding vector
            
        Returns:
            Path to saved embedding
        """
        if not settings.CACHE_EMBEDDINGS or embedding is None:
            return None
        
        embedding_path = settings.EMBEDDINGS_DIR / f"resume_{resume_id}.pkl"
        
        try:
            with open(embedding_path, 'wb') as f:
                pickle.dump(embedding, f)
            logger.info(f"Saved embedding for resume {resume_id}")
            return embedding_path
        except Exception as e:
            logger.error(f"Error saving embedding: {e}")
            return None
    
    def load_embedding(self, resume_id: int):
        """
        Load embedding from disk cache
        
        Args:
            resume_id: Resume ID
            
        Returns:
            Embedding vector or None
        """
        embedding_path = settings.EMBEDDINGS_DIR / f"resume_{resume_id}.pkl"
        
        if not embedding_path.exists():
            return None
        
        try:
            with open(embedding_path, 'rb') as f:
                embedding = pickle.load(f)
            logger.info(f"Loaded cached embedding for resume {resume_id}")
            return embedding
        except Exception as e:
            logger.error(f"Error loading embedding: {e}")
            return None
    
    def get_resume_embedding(self, resume_id: int, resume_text: str):
        """
        Get or generate embedding for resume
        
        Args:
            resume_id: Resume ID
            resume_text: Resume text
            
        Returns:
            Embedding vector or None
        """
        # Check memory cache
        if resume_id in self.embedding_cache:
            return self.embedding_cache[resume_id]
        
        # Check disk cache
        embedding = self.load_embedding(resume_id)
        
        if embedding is None:
            # Generate new embedding
            logger.info(f"Generating new embedding for resume {resume_id}")
            embedding = self.generate_embedding(resume_text)
            if embedding is not None:
                self.save_embedding(resume_id, embedding)
        
        # Store in memory cache
        if embedding is not None:
            self.embedding_cache[resume_id] = embedding
        
        return embedding
    
    @staticmethod
    def calculate_cosine_similarity(vec1, vec2) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score (0-1)
        """
        if vec1 is None or vec2 is None:
            return 0.5

        if not HAS_SKLEARN or not HAS_NUMPY:
            # Fallback: simple overlap-based similarity
            return 0.5
        
        vec1 = vec1.reshape(1, -1)
        vec2 = vec2.reshape(1, -1)
        similarity = cosine_similarity(vec1, vec2)[0][0]
        return float(similarity)
    
    @staticmethod
    def fuzzy_match_skill(skill: str, skill_list: List[str], threshold: float = 0.8) -> Tuple[bool, float, Optional[str]]:
        """
        Fuzzy match a skill against a list of skills
        
        Args:
            skill: Skill to match
            skill_list: List of skills to match against
            threshold: Minimum similarity threshold
            
        Returns:
            Tuple of (is_match, best_score, matched_skill)
        """
        if not HAS_RAPIDFUZZ:
            # Simple exact match fallback
            skill_lower = skill.lower()
            for candidate_skill in skill_list:
                if skill_lower == candidate_skill.lower():
                    return True, 1.0, candidate_skill
            return False, 0.0, None
        
        best_score = 0.0
        best_match = None
        
        skill_lower = skill.lower()
        
        for candidate_skill in skill_list:
            candidate_lower = candidate_skill.lower()
            
            # Exact match
            if skill_lower == candidate_lower:
                return True, 1.0, candidate_skill
            
            # Fuzzy match
            score = fuzz.ratio(skill_lower, candidate_lower) / 100.0
            
            if score > best_score:
                best_score = score
                best_match = candidate_skill
        
        is_match = best_score >= threshold
        return is_match, best_score, best_match if is_match else None
    
    @staticmethod
    def match_skills(required_skills: List[str], resume_skills: List[str]) -> Dict[str, Any]:
        """
        Match required skills against resume skills
        
        Args:
            required_skills: Skills required by job
            resume_skills: Skills in resume
            
        Returns:
            Dictionary with matching results
        """
        matched = []
        missing = []
        partial = []
        
        for req_skill in required_skills:
            is_match, score, matched_skill = AIMatcher.fuzzy_match_skill(
                req_skill, resume_skills, threshold=0.8
            )
            
            if is_match:
                if score >= 0.95:
                    matched.append({
                        'required': req_skill,
                        'found': matched_skill,
                        'score': score
                    })
                else:
                    partial.append({
                        'required': req_skill,
                        'found': matched_skill,
                        'score': score
                    })
            else:
                missing.append(req_skill)
        
        # Find additional skills (in resume but not required)
        additional = []
        for resume_skill in resume_skills:
            is_match, _, _ = AIMatcher.fuzzy_match_skill(
                resume_skill, required_skills, threshold=0.8
            )
            if not is_match:
                additional.append(resume_skill)
        
        return {
            'matched': matched,
            'partial': partial,
            'missing': missing,
            'additional': additional,
            'match_rate': len(matched) / len(required_skills) if required_skills else 0.0
        }
    
    @staticmethod
    def calculate_experience_score(required_years: Optional[float], resume_years: Optional[float]) -> float:
        """
        Calculate experience match score
        
        Args:
            required_years: Years required
            resume_years: Years in resume
            
        Returns:
            Score (0-1)
        """
        if required_years is None or resume_years is None:
            return 0.5  # Neutral score if information missing
        
        if resume_years >= required_years:
            return 1.0
        else:
            # Partial credit if close
            ratio = resume_years / required_years
            return max(0.0, ratio)
    
    def match_resume_to_job(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Match a single resume against a job description
        
        Args:
            resume_data: Dictionary with resume information
            job_data: Dictionary with job description information
            
        Returns:
            Dictionary with matching scores and details
        """
        logger.info(f"Matching resume {resume_data.get('id')} to job {job_data.get('job_title')}")
        
        # 1. Semantic similarity (using embeddings)
        resume_text = resume_data.get('raw_text', '')
        job_text = job_data.get('raw_text', '')
        
        resume_embedding = self.get_resume_embedding(resume_data['id'], resume_text)
        job_embedding = self.generate_embedding(job_text)
        
        semantic_similarity = self.calculate_cosine_similarity(resume_embedding, job_embedding)
        
        # 2. Skills matching
        required_skills = job_data.get('required_skills', [])
        preferred_skills = job_data.get('preferred_skills', [])
        resume_skills = resume_data.get('skills', [])
        
        required_match = self.match_skills(required_skills, resume_skills)
        preferred_match = self.match_skills(preferred_skills, resume_skills)
        
        # 3. Technical skills matching
        prog_langs_job = job_data.get('programming_languages', [])
        prog_langs_resume = resume_data.get('programming_languages', [])
        programming_match = self.match_skills(prog_langs_job, prog_langs_resume)
        
        cloud_job = job_data.get('cloud_platforms', [])
        cloud_resume = resume_data.get('cloud_platforms', [])
        cloud_match = self.match_skills(cloud_job, cloud_resume)
        
        # 4. Experience matching
        experience_score = self.calculate_experience_score(
            job_data.get('years_experience'),
            resume_data.get('total_experience')
        )
        
        # 5. Certifications matching
        certs_job = job_data.get('certifications', [])
        certs_resume = resume_data.get('certifications', [])
        cert_match = self.match_skills(certs_job, certs_resume)
        
        # 6. Calculate weighted scores
        required_skill_score = required_match['match_rate'] * 100
        preferred_skill_score = preferred_match['match_rate'] * 100
        programming_score = programming_match['match_rate'] * 100
        cloud_score = cloud_match['match_rate'] * 100
        certification_score = cert_match['match_rate'] * 100
        experience_score_pct = experience_score * 100
        
        # Overall score (weighted)
        overall_score = (
            settings.WEIGHT_REQUIRED_SKILLS * required_skill_score +
            settings.WEIGHT_PREFERRED_SKILLS * preferred_skill_score +
            settings.WEIGHT_EXPERIENCE * experience_score_pct +
            settings.WEIGHT_CERTIFICATIONS * certification_score +
            settings.WEIGHT_EDUCATION * semantic_similarity * 100
        )
        
        # Generate explanation
        explanation = self._generate_explanation(
            required_match, preferred_match, experience_score, overall_score
        )
        
        # Generate improvement suggestions
        suggestions = self._generate_suggestions(required_match, cert_match)
        
        return {
            'overall_match_score': round(overall_score, 2),
            'technical_match_score': round((programming_score + cloud_score) / 2, 2),
            'experience_match_score': round(experience_score_pct, 2),
            'cloud_match_score': round(cloud_score, 2),
            'programming_match_score': round(programming_score, 2),
            'certification_match_score': round(certification_score, 2),
            'semantic_similarity': round(semantic_similarity * 100, 2),
            'matched_skills': [m['required'] for m in required_match['matched']],
            'missing_skills': required_match['missing'],
            'additional_skills': required_match['additional'][:10],  # Limit to 10
            'partial_skills': [
                {'skill': p['required'], 'match': p['found'], 'score': round(p['score'] * 100, 1)}
                for p in required_match['partial']
            ],
            'match_explanation': explanation,
            'improvement_suggestions': suggestions
        }
    
    @staticmethod
    def _generate_explanation(
        required_match: Dict,
        preferred_match: Dict,
        experience_score: float,
        overall_score: float
    ) -> str:
        """
        Generate human-readable explanation for match
        """
        matched_count = len(required_match['matched'])
        total_required = len(required_match['matched']) + len(required_match['missing'])
        
        explanation = f"Overall match score: {overall_score:.1f}%. "
        
        if matched_count == total_required and total_required > 0:
            explanation += f"Excellent match! All {total_required} required skills are present. "
        elif matched_count > 0:
            explanation += f"Matched {matched_count} out of {total_required} required skills. "
        
        if experience_score >= 1.0:
            explanation += "Experience level exceeds requirements. "
        elif experience_score >= 0.7:
            explanation += "Experience level meets requirements. "
        else:
            explanation += "Experience level may be below requirements. "
        
        if len(preferred_match['matched']) > 0:
            explanation += f"Also has {len(preferred_match['matched'])} preferred skills. "
        
        return explanation
    
    @staticmethod
    def _generate_suggestions(required_match: Dict, cert_match: Dict) -> List[str]:
        """
        Generate improvement suggestions
        """
        suggestions = []
        
        if required_match['missing']:
            suggestions.append(
                f"Consider adding these skills: {', '.join(required_match['missing'][:5])}"
            )
        
        if cert_match['missing']:
            suggestions.append(
                f"Recommended certifications: {', '.join(cert_match['missing'][:3])}"
            )
        
        if not suggestions:
            suggestions.append("Resume looks strong! Consider highlighting specific achievements.")
        
        return suggestions
