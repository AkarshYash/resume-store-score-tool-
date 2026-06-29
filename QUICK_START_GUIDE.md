# 🚀 Quick Start Guide - AI Resume Intelligence Platform

## ⚡ Fastest Way to Run

### Option 1: Automated Launch (Recommended)

#### Step 1: Start Backend
Double-click: **`START_PROJECT.bat`**

This will:
- ✓ Create Python virtual environment
- ✓ Install all backend dependencies
- ✓ Create database
- ✓ Start backend server on http://localhost:8000

#### Step 2: Start Frontend
Open a **NEW terminal** and double-click: **`START_FRONTEND.bat`**

This will:
- ✓ Install Node.js dependencies
- ✓ Start frontend on http://localhost:5173

#### Step 3: Access Application
Open browser: **http://localhost:5173**

---

## 🛠️ Manual Setup (If automated scripts fail)

### Backend Setup

```cmd
cd backend
python -m venv venv
call venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings python-dotenv python-multipart email-validator aiofiles
python run.py
```

### Frontend Setup (in new terminal)

```cmd
cd frontend
npm install
npm run dev
```

---

## 📝 What You Can Do

### 1️⃣ Add Candidates
- Go to "Candidates" page
- Click "Add Candidate"
- Enter name (e.g., "Nirav")

### 2️⃣ Upload Resumes
- Click on a candidate
- Upload multiple specialized resumes:
  - `Nirav_Python_GenAI.docx`
  - `Nirav_AWS_Architect.pdf`
  - `Nirav_Data_Engineer.docx`
  - etc.

### 3️⃣ Match Jobs
- Go to "Matching" page
- Paste a Job Description or enter Job Title
- Click "Find Best Match"
- See ranked results with match scores

### 4️⃣ View Analytics
- Go to "Analytics" page
- See skills distribution
- View technology trends
- Check match statistics

---

## 🔧 Troubleshooting

### Backend won't start?

**Issue**: Dependencies failed to install
**Solution**:
```cmd
cd backend
call venv\Scripts\activate
pip cache purge
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings python-dotenv python-multipart email-validator aiofiles
```

**Issue**: Python not found
**Solution**: Install Python 3.10+ from https://python.org

### Frontend won't start?

**Issue**: Node.js not found
**Solution**: Install Node.js 18+ from https://nodejs.org

**Issue**: npm install fails
**Solution**:
```cmd
cd frontend
npm cache clean --force
npm install --legacy-peer-deps
```

### Port already in use?

**Backend (8000)**:
```cmd
netstat -ano | findstr :8000
taskkill /F /PID <PID>
```

**Frontend (5173)**:
Change port in `frontend/vite.config.ts`:
```ts
export default defineConfig({
  server: {
    port: 3000  // Use different port
  }
})
```

### Database errors?

Delete the old database and recreate:
```cmd
cd backend
del resume_intelligence.db
python -c "from app.database import init_db; init_db()"
```

---

## 📊 System Requirements

- **Python**: 3.10 or higher
- **Node.js**: 18 or higher
- **RAM**: 2GB minimum (4GB recommended)
- **Disk Space**: 500MB minimum
- **OS**: Windows 10/11

---

## 🌐 Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

---

## 📂 Project Structure

```
Resume store/
├── backend/           # Python FastAPI backend
│   ├── app/           # Application code
│   ├── uploads/       # Uploaded resumes
│   ├── venv/          # Virtual environment
│   └── run.py         # Server startup
├── frontend/          # React TypeScript frontend
│   ├── src/           # Source code
│   └── package.json   # Dependencies
├── START_PROJECT.bat  # Backend launcher
├── START_FRONTEND.bat # Frontend launcher
└── README.md          # Documentation
```

---

## ✅ Success Checklist

- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Can access http://localhost:5173
- [ ] Can add candidates
- [ ] Can upload resumes
- [ ] Can match jobs

---

## 🎯 Next Steps

1. **Add Your Resumes**: Upload PDF/DOCX files for each candidate
2. **Test Matching**: Try matching with sample job descriptions
3. **Explore Features**: Check out Analytics, Search, and Comparison features
4. **Customize**: Modify the code to fit your specific needs

---

## 💡 Tips

- **Multiple Resumes**: Each candidate can have unlimited specialized resumes
- **Automatic Parsing**: Skills are extracted automatically from resumes
- **Smart Matching**: AI finds the BEST resume, not just best candidate
- **Real-time**: All matching happens instantly on your local machine
- **100% Free**: No API keys, no subscriptions, no limits

---

## 📞 Need Help?

Check the main README.md for detailed documentation, or refer to:
- `docs/SETUP.md` - Detailed setup guide
- `docs/API.md` - API documentation
- Backend logs - Check terminal for errors
- Browser console - Check for frontend errors

---

**Built with ❤️ using 100% free and open-source technologies**
