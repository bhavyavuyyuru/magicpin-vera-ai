# DEPLOYMENT GUIDE FOR MAGICPIN AI CHALLENGE

## OPTION 1: Deploy to Render.com (RECOMMENDED - Easiest)

### Step 1: Prepare Your Files
You already have these files ready:
- ✅ app.py (Flask server)
- ✅ requirements.txt (dependencies)
- ✅ Procfile (deployment config)
- ✅ submission.jsonl (30 test messages)
- ✅ README.md (approach)
- ✅ dataset/ folder (all data)

### Step 2: Create GitHub Repository
1. Go to https://github.com/new
2. Create new repo (name: "magicpin-vera-ai")
3. Clone to your machine:
   ```
   git clone https://github.com/YOUR_USERNAME/magicpin-vera-ai.git
   cd magicpin-vera-ai
   ```
4. Copy all your files into this folder
5. Push to GitHub:
   ```
   git add .
   git commit -m "Magicpin Vera AI Challenge submission"
   git push origin main
   ```

### Step 3: Deploy to Render.com
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub account
4. Select your "magicpin-vera-ai" repo
5. Fill in:
   - **Name**: magicpin-vera-challenge
   - **Environment**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
6. Click "Create Web Service"
7. **Wait 3-5 minutes** for deployment
8. **Get your public URL**: https://magicpin-vera-challenge.onrender.com

### Step 4: Test Your Public URL
Once deployed, test these:
```
https://magicpin-vera-challenge.onrender.com/v1/healthz
https://magicpin-vera-challenge.onrender.com/v1/metadata
```

---

## OPTION 2: Deploy to Railway.app (Alternative)

1. Go to https://railway.app
2. Click "New Project"
3. Choose "Deploy from GitHub"
4. Connect your repo
5. Railway auto-detects Python + Procfile
6. **Auto-deploys** → Get public URL

---

## OPTION 3: Deploy to PythonAnywhere (No Git Required)

1. Go to https://www.pythonanywhere.com
2. Sign up (free tier available)
3. Upload your files via Web
4. Create new Web app → Select Flask
5. Point to app.py
6. Get URL like: https://yourusername.pythonanywhere.com

---

## OPTION 4: Local Testing Before Deployment

Run locally to verify:
```bash
pip install -r requirements.txt
python app.py
```

Then test:
```bash
curl http://localhost:5000/v1/healthz
curl http://localhost:5000/v1/metadata
```

---

## After Deployment

### Test Endpoints
Your public bot will respond to:
- `GET /v1/healthz` → Health check
- `GET /v1/metadata` → Team info  
- `POST /v1/context` → Receive context updates
- `POST /v1/tick` → Trigger message generation
- `POST /v1/reply` → Handle merchant replies

### Submit to Challenge
Go to: https://magicpin.com/vera/ai-challenge

Upload:
1. Your public URL: `https://magicpin-vera-challenge.onrender.com`
2. File: `submission.jsonl` (30 test messages)
3. File: `README.md` (your approach)

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'flask'"**
→ Render couldn't install requirements.txt
→ Check requirements.txt has: flask, gunicorn

**"application failed to start"**
→ Check app.py for errors: `python app.py` locally first

**"Connection refused to deploy URL"**
→ Wait 5-10 minutes for cold start
→ Check logs in Render dashboard

---

## Your Current Status
✅ Code ready: app.py
✅ API endpoints implemented: 5 endpoints
✅ Bot composition refined: Specific + compelling messages
✅ Test data: 30 messages in submission.jsonl
✅ Documentation: README.md

**NEXT STEP**: Push to GitHub → Deploy to Render → Get public URL → Submit!