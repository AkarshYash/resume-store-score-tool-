# 🚀 Quick Reference Guide

## 🎯 What You Have

A complete **AI Resume Intelligence Platform** that helps you:
- Store multiple specialized resumes for each candidate
- Find the BEST RESUME for any job description
- **Preview resumes instantly without downloading** ✨ NEW
- Track trending tech stacks in job market
- Download resumes with one click

---

## 🆕 Latest Feature: Resume Preview (Quick View)

**What it does**: View resumes instantly in a modal window, just like Mac's Quick Look!

**How to use**:
1. Go to Candidates or All Resumes page
2. Click the **eye icon (👁️)** on any resume
3. Resume opens in a large modal window
4. **PDF files**: Full preview, scroll through entire document
5. **DOCX files**: Download option (browser can't preview Word docs)
6. Click **X** or **ESC** to close
7. Click **Download button** to save the file

**Benefits**:
- ✅ No download needed for quick viewing
- ✅ Faster screening of multiple resumes
- ✅ Compare resumes quickly
- ✅ Professional UI experience

---

## 🌐 URLs (Currently Running)

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🎨 Main Features

### 1. Candidates Page
**What it does**: Manage candidates and upload resumes

**Actions**:
- **Add Candidate**: Red "+ Add Candidate" button (top right)
- **Single Upload**: Click "Single" on any candidate card
- **Bulk Upload**: Click "Bulk" on any candidate card ✨ NEW
- **View Resumes**: Click eye icon
- **Delete**: Click trash icon

### 2. All Resumes Page ✨ NEW
**What it does**: View ALL resumes from ALL candidates in one place

**Actions**:
- **Search**: Type in search box (searches name, skills, candidate)
- **Download**: Click green "Download" button
- **Sort**: Resumes shown newest first

### 3. Matching Page
**What it does**: Find best resume for a job

**Actions**:
- Paste job description
- Click "Find Best Match"
- See ranked resumes with scores
- Download the top match

### 4. JD Analytics Page ✨ NEW
**What it does**: Track trending technologies in job market

**Actions**:
- Paste job descriptions as you receive them
- System analyzes tech requirements
- View bar chart of top 15 technologies
- View pie chart of category distribution
- Filter by: This week / 30 days / 90 days

### 5. Analytics Page
**What it does**: Overview statistics

**Shows**:
- Total candidates
- Total resumes
- Recent searches
- Top skills
- Recent uploads

---

## 📤 Bulk Upload Workflow ✨

1. Go to **Candidates** page
2. Click **Bulk** button on any candidate
3. Click **Choose Files** or drag & drop
4. Select multiple PDF/DOCX files (hold Ctrl/Cmd)
5. System auto-extracts names:
   - "Nirav_Python_GenAI.pdf" → "Python GenAI"
   - "Nirav_AWS_Architect.docx" → "AWS Architect"
6. Edit any names you want to change
7. Click **Upload All (X files)**
8. Wait for success message
9. Done! All resumes uploaded

---

## 📥 Download Resume Workflow ✨

**Method 1 - From Candidate View**:
1. Go to Candidates page
2. Click eye icon on candidate
3. Click green "Download" button on any resume

**Method 2 - From All Resumes**:
1. Go to All Resumes page
2. Find the resume you want
3. Click green "Download" button

---

## 📊 JD Analytics Workflow ✨

**Daily Use**:
1. Receive job description via email
2. Open JD Analytics page
3. Paste JD text into "Job Description Text" field
4. Click "Analyze Tech Stack"
5. System stores it and shows:
   - Role type (GenAI Engineer, Cloud Engineer, etc.)
   - Technologies found (Python, AWS, React, etc.)
   - Experience required
6. Charts update automatically showing trends

**View Trends**:
- Top bar chart shows most mentioned technologies
- Pie chart shows category distribution
- Filter by time: This week / 30 days / 90 days

---

## 🔧 Restart Servers

If you need to restart:

**Frontend**:
```cmd
cd "c:\Users\chatu\OneDrive\Desktop\Resume store\frontend"
npm run dev
```

**Backend**:
```cmd
cd "c:\Users\chatu\OneDrive\Desktop\Resume store"
cd backend
call backend\venv\Scripts\activate
python run.py
```

---

## 📁 Where Files Are Stored

- **Database**: `backend/resume_intelligence.db` (SQLite)
- **Uploaded Resumes**: `backend/uploads/CANDIDATE_NAME/filename.pdf`
- **Logs**: `backend/server.out.log` and `backend/server.err.log`

---

## 🎯 Common Tasks

### Add a New Candidate
1. Candidates page
2. Click "+ Add Candidate"
3. Enter name (required)
4. Optionally add email, phone, location
5. Click "Add Candidate"

### Upload First Resume
1. Click "Single" on candidate card
2. Enter resume name (e.g., "Python Developer")
3. Select PDF or DOCX file
4. Click "Upload"

### Find Best Resume for a Job
1. Go to Matching page
2. Paste job description
3. Click "Find Best Match"
4. Top result = best resume to use
5. Click download to get the file

### Track Tech Trends
1. Go to JD Analytics page
2. Paste each JD you receive
3. Click "Analyze Tech Stack"
4. Check charts weekly to see trends

---

## 🐛 Troubleshooting

### Frontend won't load
- Check http://localhost:5173 is accessible
- Restart: `cd frontend && npm run dev`
- Check `frontend/vite.err.log` for errors

### Backend won't load
- Check http://localhost:8000/docs is accessible
- Restart: `cd backend && python run.py`
- Check `backend/server.err.log` for errors

### Can't upload files
- Check file is PDF or DOCX
- File must be < 10MB
- Check `backend/uploads/` folder exists

### Download not working
- File must exist in `backend/uploads/`
- Check browser download settings
- Try different browser

### AI matching not working
- App works with basic keyword matching (default)
- For full AI: Install dependencies:
  ```cmd
  cd backend
  call backend\venv\Scripts\activate
  pip install PyMuPDF python-docx numpy scikit-learn sentence-transformers rapidfuzz
  ```
- Restart backend after installation

---

## 💡 Pro Tips

1. **Name Resumes Clearly**: Use descriptive names like "Python GenAI", "AWS Cloud Architect"
2. **Upload Multiple Versions**: Upload different resume versions for different roles
3. **Track All JDs**: Paste every JD you receive to build trend data
4. **Use Bulk Upload**: Saves time when adding multiple resumes
5. **Check Analytics Weekly**: See which skills are trending
6. **Keep Database Backup**: Copy `resume_intelligence.db` regularly

---

## 🚀 Deploy to Production

When ready to deploy online:
1. Read **DEPLOYMENT_GUIDE.md**
2. Push code to GitHub
3. Deploy backend to Render (free)
4. Deploy frontend to Cloudflare Pages (free)
5. Update CORS settings
6. Done!

**Deployment time**: 20-30 minutes

---

## 📞 Quick Help

**Documentation Files**:
- **STATUS.md** - Complete feature list and project status
- **DEPLOYMENT_GUIDE.md** - Step-by-step deployment instructions
- **QUICKSTART.md** - Original quick start guide
- **README.md** - Project overview

**API Documentation**:
- Visit http://localhost:8000/docs for interactive API docs
- All endpoints documented with examples

---

## ✅ Current Status

✅ Backend: Running on http://localhost:8000
✅ Frontend: Running on http://localhost:5173
✅ Database: Created and initialized
✅ All features: 100% complete
✅ Ready to use: YES
✅ Ready to deploy: YES

---

**Enjoy your AI Resume Intelligence Platform! 🎉**

Need help? Check the documentation files or the API docs at http://localhost:8000/docs
