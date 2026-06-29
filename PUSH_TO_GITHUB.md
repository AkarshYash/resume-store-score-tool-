# 🚀 PUSH TO GITHUB & DEPLOY - 2 MINUTES!

## ✅ Code is Ready! Just Push!

Everything is committed and ready. Now push to GitHub:

## 📤 Push to GitHub

Run these commands:

```cmd
cd "c:\Users\chatu\OneDrive\Desktop\Resume store"
git push -u origin main
```

**If it asks for credentials**:
- Use GitHub username: `AkarshYash`
- Use Personal Access Token (not password)
- Get token from: https://github.com/settings/tokens

---

## 🚀 Deploy on Render (5 Minutes)

### Backend Deployment:

1. **Go to Render**: https://render.com
2. **Sign in with GitHub**
3. Click **"New +"** → **"Web Service"**
4. **Connect Repository**: `AkarshYash/resume-store-score-tool-`
5. **Configure**:
   - **Name**: `resume-intelligence-api`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
6. Click **"Create Web Service"**
7. Wait 5 minutes - Render will build and deploy
8. **Copy your backend URL**: `https://resume-intelligence-api.onrender.com`

### Frontend Deployment:

1. **Build frontend locally first**:
```cmd
cd "c:\Users\chatu\OneDrive\Desktop\Resume store\frontend"
npm run build
```

2. **Deploy to Netlify** (Easiest):
   - Go to https://app.netlify.com/drop
   - Drag the `frontend/dist` folder
   - Done! Get URL like: `https://resume-intelligence.netlify.app`

**OR use Vercel**:
   - Go to https://vercel.com/new
   - Import GitHub repo
   - Root directory: `frontend`
   - Framework: Vite
   - Deploy!

3. **Update Frontend to Connect to Backend**:
   - Edit `frontend/.env`:
   ```
   VITE_API_URL=https://resume-intelligence-api.onrender.com
   ```
   - Rebuild: `npm run build`
   - Re-upload to Netlify/Vercel

### Update CORS:

Edit `backend/app/config.py` and add your frontend URL:
```python
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://resume-intelligence.netlify.app",  # Your frontend URL
    "https://*.netlify.app",
    "https://*.vercel.app"
]
```

Commit and push - Render will auto-redeploy!

---

## 🎯 Your Live URLs

After deployment you'll have:
- **Frontend**: https://resume-intelligence.netlify.app
- **Backend API**: https://resume-intelligence-api.onrender.com
- **API Docs**: https://resume-intelligence-api.onrender.com/docs

Share the frontend URL with anyone!

---

## 🆘 Quick Alternative - Railway (Even Faster!)

If you want ONE-CLICK deployment:

1. **Install Railway CLI**:
```cmd
npm install -g @railway/cli
```

2. **Login and Deploy**:
```cmd
cd "c:\Users\chatu\OneDrive\Desktop\Resume store"
railway login
railway init
railway up
```

3. **Done!** Railway auto-deploys everything and gives you URLs!

---

## 📋 Summary

**What you have**:
- ✅ Code committed to Git
- ✅ Ready to push to GitHub
- ✅ All config files created
- ✅ 30 resumes in database
- ✅ All features working

**What to do**:
1. Push to GitHub (1 command)
2. Deploy on Render/Netlify (5 minutes)
3. Get live URL!

**Run this now**:
```cmd
git push -u origin main
```

Then go to Render.com and deploy!
