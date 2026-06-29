"""
Resume parsing service - extracts text and information from PDF and DOCX files
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

# Optional imports for PDF/DOCX parsing
try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False
    logging.warning("PyMuPDF (fitz) not installed. PDF parsing will be limited.")

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False
    logging.warning("python-docx not installed. DOCX parsing will be limited.")

logger = logging.getLogger(__name__)


class ResumeParser:
    """
    Parse resumes and extract structured information
    """
    
    # Common skill patterns
    SKILLS_KEYWORDS = {
        'programming_languages': [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'golang',
            'ruby', 'php', 'swift', 'kotlin', 'rust', 'scala', 'r', 'matlab',
            'perl', 'shell', 'bash', 'powershell'
        ],
        'frameworks': [
            'react', 'angular', 'vue', 'svelte', 'django', 'flask', 'fastapi',
            'spring', 'springboot', 'express', 'nodejs', 'node.js', 'nest',
            'nextjs', 'next.js', 'nuxt', 'laravel', 'rails', 'asp.net', '.net',
            'hibernate', 'struts', 'jquery'
        ],
        'databases': [
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
            'dynamodb', 'oracle', 'sql server', 'mariadb', 'sqlite', 'neo4j',
            'couchdb', 'influxdb', 'firebase', 'snowflake', 'bigquery'
        ],
        'cloud_platforms': [
            'aws', 'amazon web services', 'azure', 'microsoft azure', 'gcp',
            'google cloud', 'ibm cloud', 'oracle cloud', 'digitalocean',
            'heroku', 'netlify', 'vercel', 'cloudflare'
        ],
        'cloud_services': [
            's3', 'ec2', 'lambda', 'rds', 'dynamodb', 'cloudfront', 'route53',
            'eks', 'ecs', 'fargate', 'sqs', 'sns', 'kinesis',
            'azure functions', 'azure blob', 'azure sql', 'cosmos db',
            'cloud functions', 'cloud storage', 'cloud sql', 'gke', 'cloud run'
        ],
        'devops_tools': [
            'docker', 'kubernetes', 'k8s', 'jenkins', 'gitlab', 'github actions',
            'circleci', 'travis', 'terraform', 'ansible', 'chef', 'puppet',
            'helm', 'argocd', 'grafana', 'prometheus', 'datadog', 'splunk',
            'elk', 'nginx', 'apache', 'vagrant', 'packer'
        ],
        'ai_ml': [
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
            'opencv', 'nltk', 'spacy', 'huggingface', 'transformers', 'bert',
            'gpt', 'llm', 'langchain', 'openai', 'anthropic', 'machine learning',
            'deep learning', 'neural networks', 'computer vision', 'nlp',
            'natural language processing', 'rag', 'vector database', 'pinecone',
            'weaviate', 'chromadb', 'faiss'
        ],
        'data_tools': [
            'spark', 'hadoop', 'kafka', 'airflow', 'dbt', 'tableau', 'power bi',
            'looker', 'databricks', 'snowflake', 'etl', 'data warehouse'
        ]
    }
    
    @staticmethod
    def extract_text_from_pdf(file_path: Path) -> str:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        if not HAS_FITZ:
            logger.warning("PyMuPDF not installed. Cannot parse PDF files.")
            return f"[PDF parsing not available - install PyMuPDF]\nFile: {file_path.name}"
        
        try:
            text = ""
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
            logger.info(f"Extracted {len(text)} characters from PDF: {file_path.name}")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            raise
    
    @staticmethod
    def extract_text_from_docx(file_path: Path) -> str:
        """
        Extract text from DOCX file
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            Extracted text
        """
        if not HAS_DOCX:
            logger.warning("python-docx not installed. Cannot parse DOCX files.")
            return f"[DOCX parsing not available - install python-docx]\nFile: {file_path.name}"
        
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            logger.info(f"Extracted {len(text)} characters from DOCX: {file_path.name}")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {file_path}: {e}")
            raise
    
    @classmethod
    def extract_text(cls, file_path: Path) -> str:
        """
        Extract text from resume file (PDF or DOCX)
        
        Args:
            file_path: Path to resume file
            
        Returns:
            Extracted text
        """
        file_ext = file_path.suffix.lower()
        
        if file_ext == '.pdf':
            return cls.extract_text_from_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            return cls.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    @staticmethod
    def extract_email(text: str) -> Optional[str]:
        """
        Extract email address from text
        
        Args:
            text: Resume text
            
        Returns:
            Email address or None
        """
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    @staticmethod
    def extract_phone(text: str) -> Optional[str]:
        """
        Extract phone number from text
        
        Args:
            text: Resume text
            
        Returns:
            Phone number or None
        """
        # Common phone patterns
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        return None
    
    @staticmethod
    def extract_experience_years(text: str) -> Optional[float]:
        """
        Extract years of experience from text
        
        Args:
            text: Resume text
            
        Returns:
            Years of experience or None
        """
        # Patterns for experience
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience[:\s]+(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?\s+(?:of\s+)?experience',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    return float(matches[0])
                except ValueError:
                    continue
        
        # Try to estimate from work history dates
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, text)
        if len(years) >= 2:
            years = [int(y) for y in years]
            experience = max(years) - min(years)
            return float(experience) if experience > 0 and experience < 50 else None
        
        return None
    
    @classmethod
    def extract_skills(cls, text: str, skill_category: str) -> List[str]:
        """
        Extract skills from text for a specific category
        
        Args:
            text: Resume text
            skill_category: Category of skills to extract
            
        Returns:
            List of found skills
        """
        text_lower = text.lower()
        skills_found = []
        
        if skill_category in cls.SKILLS_KEYWORDS:
            for skill in cls.SKILLS_KEYWORDS[skill_category]:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    # Add the skill with proper capitalization
                    skills_found.append(skill.title())
        
        return list(set(skills_found))  # Remove duplicates
    
    @classmethod
    def extract_all_skills(cls, text: str) -> Dict[str, List[str]]:
        """
        Extract all skills from text
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary of skill categories and their values
        """
        return {
            'programming_languages': cls.extract_skills(text, 'programming_languages'),
            'frameworks': cls.extract_skills(text, 'frameworks'),
            'databases': cls.extract_skills(text, 'databases'),
            'cloud_platforms': cls.extract_skills(text, 'cloud_platforms'),
            'cloud_services': cls.extract_skills(text, 'cloud_services'),
            'devops_tools': cls.extract_skills(text, 'devops_tools'),
            'ai_ml': cls.extract_skills(text, 'ai_ml'),
            'data_tools': cls.extract_skills(text, 'data_tools'),
        }
    
    @staticmethod
    def extract_certifications(text: str) -> List[str]:
        """
        Extract certifications from text
        
        Args:
            text: Resume text
            
        Returns:
            List of certifications
        """
        cert_keywords = [
            'aws certified', 'azure certified', 'gcp certified', 'google cloud certified',
            'certified kubernetes', 'ckad', 'cka', 'terraform certified',
            'pmp', 'cissp', 'comptia', 'ccna', 'ccnp', 'mcsa', 'mcse',
            'oracle certified', 'java certified', 'scrum master', 'csm',
            'professional scrum', 'pmi', 'itil', 'togaf'
        ]
        
        certifications = []
        text_lower = text.lower()
        
        for cert in cert_keywords:
            if cert in text_lower:
                certifications.append(cert.title())
        
        return list(set(certifications))
    
    @staticmethod
    def extract_companies(text: str) -> List[str]:
        """
        Extract company names from text (basic implementation)
        
        Args:
            text: Resume text
            
        Returns:
            List of company names
        """
        # Common company indicators
        company_patterns = [
            r'(?:at|@)\s+([A-Z][A-Za-z\s&.]+(?:Inc|LLC|Ltd|Corp|Corporation)?)',
            r'([A-Z][A-Za-z\s&.]+(?:Inc|LLC|Ltd|Corp|Corporation))',
        ]
        
        companies = []
        for pattern in company_patterns:
            matches = re.findall(pattern, text)
            companies.extend(matches)
        
        # Filter out common false positives
        filtered = [c.strip() for c in companies if len(c.strip()) > 2]
        return list(set(filtered))[:10]  # Limit to 10
    
    @classmethod
    def parse_resume(cls, file_path: Path) -> Dict[str, Any]:
        """
        Parse resume and extract all information
        
        Args:
            file_path: Path to resume file
            
        Returns:
            Dictionary with parsed information
        """
        logger.info(f"Parsing resume: {file_path.name}")
        
        # Extract text
        text = cls.extract_text(file_path)
        
        # Extract all information
        skills = cls.extract_all_skills(text)
        
        # Combine all skills for a master list
        all_skills = []
        for skill_list in skills.values():
            all_skills.extend(skill_list)
        all_skills = list(set(all_skills))
        
        parsed_data = {
            'raw_text': text,
            'email': cls.extract_email(text),
            'phone': cls.extract_phone(text),
            'total_experience': cls.extract_experience_years(text),
            'skills': all_skills,
            'programming_languages': skills['programming_languages'],
            'frameworks': skills['frameworks'],
            'databases': skills['databases'],
            'cloud_platforms': skills['cloud_platforms'] + skills['cloud_services'],
            'devops_tools': skills['devops_tools'],
            'ai_ml_skills': skills['ai_ml'],
            'certifications': cls.extract_certifications(text),
            'companies': cls.extract_companies(text),
        }
        
        logger.info(f"Parsed resume successfully. Found {len(all_skills)} skills")
        return parsed_data

    @staticmethod
    def infer_resume_title(file_name: str, text: str = "") -> str:
        """
        Build an editable resume title from the document content first, then filename.
        This keeps uploads fast while avoiding titles like "Nirav Patel Resume Final".
        """
        stem = Path(file_name).stem
        source = f"{stem}\n{text[:2000]}"
        tokens = re.split(r"[_\-\s/|]+", source)
        stop_words = {
            "resume", "cv", "curriculum", "vitae", "updated", "final", "latest",
            "new", "master", "copy", "doc", "docx", "pdf", "nirav", "patel",
            "foram"
        }
        role_words = [
            "python", "java", "javascript", "typescript", "genai", "ai", "ml",
            "data", "engineer", "developer", "architect", "devops", "cloud",
            "aws", "azure", "gcp", "databricks", "terraform", "fullstack",
            "backend", "frontend", "react", "angular", "kubernetes", "security"
        ]

        picked = []
        lower_source = source.lower()
        for word in role_words:
            if re.search(r"\b" + re.escape(word) + r"\b", lower_source):
                picked.append(word)

        if not picked:
            for token in tokens:
                clean = re.sub(r"[^A-Za-z0-9+#.]", "", token).strip()
                if clean and clean.lower() not in stop_words and len(clean) > 1:
                    picked.append(clean.lower())
                if len(picked) >= 4:
                    break

        title = " ".join(dict.fromkeys(picked[:5])) or stem
        replacements = {
            "genai": "GenAI",
            "ai": "AI",
            "ml": "ML",
            "aws": "AWS",
            "gcp": "GCP",
            "devops": "DevOps",
            "fullstack": "Full Stack",
        }
        return " ".join(replacements.get(part, part.title()) for part in title.split())
