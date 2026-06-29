# 🚀 Quick Start Guide

## Prerequisites

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)

---

## Option 1: Automated Setup (Windows)

### Step 1: Run Setup Script
```bash
setup_windows.bat
```

This will:
- ✅ Create Python virtual environment
- ✅ Install all dependencies
- ✅ Setup database
- ✅ Download AI models

### Step 2: Start Backend
```bash
start_backend.bat
```

Backend will run at: **http://localhost:8000**

### Step 3: Start Frontend (New Terminal)
```bash
cd frontend
npm install
npm run dev
```

Frontend will run at: **http://localhost:5173**

---

## Option 2: Manual Setup

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Setup database
python ../scripts/setup_database.py

# Download AI models (optional - will download on first use)
python ../scripts/download_models.py

# Start server
python run.py
```

### Frontend Setup

```bash
# Navigate to frontend (new terminal)
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## Access the Application

Once both servers are running:

- 🌐 **Frontend**: http://localhost:5173
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs

---

## First Steps in the Application

### 1. Create a Candidate
- Go to **Candidates** page
- Click "Add Candidate"
- Enter name and details
- Click "Create"

### 2. Upload Resumes
- Click on the candidate
- Upload PDF or DOCX files
- Multiple resumes per candidate are supported
- Example naming:
  - `Nirav_Python_GenAI.pdf`
  - `Nirav_AWS_Architect.docx`
  - `Nirav_Data_Engineer.pdf`

### 3. Match Resumes to a Job
- Go to **Matching** page
- Paste a job description OR
- Upload a JD file OR
- Enter just a job title
- Click "Find Matches"
- View ranked results with match scores!

---

## Example Job Description

Try this sample JD:

```
Senior Python GenAI Engineer

Required Skills:
- Python
- LangChain
- OpenAI
- AWS
- Vector Database
- RAG
- FastAPI

Experience: 5+ years

We're looking for an experienced Python engineer with expertise in Generative AI...
```

---

## Troubleshooting

### Backend won't start

**Problem**: `ModuleNotFoundError`

**Solution**:
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### Port already in use

**Backend (port 8000)**:
```bash
uvicorn app.main:app --reload --port 8001
```

**Frontend (port 5173)**:
```bash
npm run dev -- --port 3000
```

### AI models not downloading

Models will auto-download on first use. Be patient, it may take 5-10 minutes.

Manual download:
```bash
cd backend
venv\Scripts\activate
python ../scripts/download_models.py
```

---

## Project Structure

```
resume-intelligence-platform/
├── backend/          # FastAPI backend
│   ├── app/         # Application code
│   ├── uploads/     # Resume storage
│   └── embeddings/  # AI embeddings cache
├── frontend/        # React frontend
│   └── src/         # Source code
├── docs/            # Documentation
└── scripts/         # Setup scripts
```

---

## What Makes This Special?

✅ **100% Free** - No paid APIs, no subscriptions  
✅ **AI-Powered** - Semantic matching using Sentence Transformers  
✅ **Multi-Resume Support** - Each candidate can have unlimited specialized resumes  
✅ **Instant Results** - Get ranked matches in seconds  
✅ **Detailed Analysis** - See matched skills, missing skills, and improvement suggestions  
✅ **Export Ready** - Download reports and share results  

---

## Tech Stack

**Backend**: Python, FastAPI, SQLAlchemy, SQLite  
**AI**: Sentence Transformers, scikit-learn, spaCy  
**Frontend**: React, TypeScript, Tailwind CSS  
**Parsing**: PyMuPDF, python-docx  

---

## Need Help?

- 📖 Read the [Full Setup Guide](docs/SETUP.md)
- 🔧 Check [API Documentation](docs/API.md)
- 🏗️ See [Architecture Guide](docs/ARCHITECTURE.md)

---

**Built with ❤️ using 100% free and open-source technologies**

No OpenAI API | No Paid Services | Runs Completely Local
