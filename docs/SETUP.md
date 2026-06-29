# Setup Guide - Resume Intelligence Platform

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10 or higher** ([Download](https://www.python.org/downloads/))
- **Node.js 18 or higher** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))

## Backend Setup (FastAPI + Python)

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- SQLAlchemy (database ORM)
- Sentence Transformers (AI matching)
- PyMuPDF & python-docx (document parsing)
- And all other dependencies

**Note:** Installation may take 5-10 minutes due to AI model downloads.

### Step 4: Download AI Models

```bash
python ../scripts/download_models.py
```

This downloads:
- Sentence Transformer model (~80MB)
- spaCy language model (~12MB)

### Step 5: Setup Database

```bash
python ../scripts/setup_database.py
```

This creates:
- SQLite database file
- All necessary tables
- Initial schema

### Step 6: Configure Environment

```bash
copy .env.example .env
```

Edit `.env` if needed (default settings work fine for development).

### Step 7: Start Backend Server

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Test Backend

Open http://localhost:8000/docs in your browser. You should see the API documentation.

---

## Frontend Setup (React + TypeScript)

### Step 1: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 2: Install Dependencies

```bash
npm install
```

This installs:
- React 18
- TypeScript
- Tailwind CSS
- Vite (build tool)

### Step 3: Start Development Server

```bash
npm run dev
```

The application will be available at:
- **Frontend**: http://localhost:5173

### Test Frontend

Open http://localhost:5173 in your browser. You should see the dashboard.

---

## Quick Start (Both Servers)

### Terminal 1 - Backend
```bash
cd backend
venv\Scripts\activate  # or source venv/bin/activate on macOS/Linux
uvicorn app.main:app --reload
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

### Access Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Troubleshooting

### Python Module Not Found

**Problem:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
```bash
cd backend
python -m pip install -r requirements.txt
```

### Port Already in Use

**Problem:** `Address already in use: 8000`

**Solution:** Kill the process using the port or use a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

### Database Locked

**Problem:** `database is locked`

**Solution:** Close all applications using the database and restart:
```bash
python scripts/setup_database.py
```

### AI Model Download Fails

**Problem:** `Connection timeout` or `Download failed`

**Solution:** Models will be downloaded automatically on first use. Or download manually:
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
python -m spacy download en_core_web_sm
```

### CORS Errors in Frontend

**Problem:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution:** Ensure backend `.env` has:
```
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## First Usage

### 1. Create a Candidate

Go to **Candidates** page and click **"Add Candidate"**:
- Name: John Doe
- Email: john@example.com
- Click **Create**

### 2. Upload Resumes

Click on the candidate and upload multiple resumes:
- John_Python_Resume.pdf
- John_AWS_Resume.docx
- John_Data_Engineer.pdf

The system will automatically parse and extract skills.

### 3. Match Resumes to a Job

Go to **Matching** page:
- Paste a job description or enter a job title
- Click **Find Matches**
- View ranked results with match scores

### 4. View Analytics

Go to **Analytics** page to see:
- Top skills across all resumes
- Cloud platform distribution
- Programming language statistics

---

## Next Steps

- Read [API Documentation](API.md)
- See [Deployment Guide](DEPLOYMENT.md)
- Check [Architecture Overview](ARCHITECTURE.md)

---

## Development Commands

### Backend

```bash
# Run tests
pytest tests/ -v

# Format code
black app/

# Type checking
mypy app/

# Lint
flake8 app/
```

### Frontend

```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint

# Type check
npm run type-check
```

---

## System Requirements

### Minimum
- CPU: Dual-core 2GHz
- RAM: 4GB
- Disk: 2GB free space
- OS: Windows 10, macOS 10.15+, or Linux

### Recommended
- CPU: Quad-core 2.5GHz+
- RAM: 8GB+
- Disk: 5GB free space
- SSD recommended for better performance

---

## Need Help?

- Check the [README.md](../README.md) for overview
- Read the [API Documentation](API.md)
- Review error logs in terminal

---

**Built with ❤️ using 100% free and open-source technologies**
