# STEP-BY-STEP: Deploy to Render.com

## Step 1: Create GitHub Repository
1. Go to https://github.com/new
2. **Repository name**: `magicpin-vera-ai-challenge`
3. **Description**: Magicpin AI Challenge - Vera Bot
4. **Public** (check the box)
5. Click **"Create repository"**

## Step 2: Upload Files to GitHub
1. In your GitHub repo, click **"Add file"** → **"Upload files"**
2. Upload these files:
   - `app.py`
   - `requirements.txt`
   - `Procfile`
   - `README.md`
   - `submission.jsonl`
   - `dataset/` folder (drag the entire folder)
3. **Commit message**: "Initial commit - Magicpin Vera AI Challenge"
4. Click **"Commit changes"**

## Step 3: Create Render Account
1. Go to https://render.com
2. Click **"Sign up"** (use GitHub login for speed)
3. Verify your email

## Step 4: Deploy Your App
1. Click **"New +"** → **"Web Service"**
2. Click **"Connect GitHub"**
3. Authorize Render to access your GitHub
4. Search for your repo: `magicpin-vera-ai-challenge`
5. Click **"Connect"**

## Step 5: Configure Deployment
1. **Name**: `magicpin-vera-ai` (or any name)
2. **Environment**: `Python 3`
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `gunicorn app:app`
5. **Instance Type**: `Free` (default)
6. Click **"Create Web Service"**

## Step 6: Wait for Deployment
- Render will show: "Building..." (takes 3-5 minutes)
- You'll see logs in real-time
- When done, you'll get: **"Your service is live at: https://magicpin-vera-ai.onrender.com"**

## Step 7: Test Your Public URL
Open a new browser tab and test:
```
https://magicpin-vera-ai.onrender.com/v1/healthz
https://magicpin-vera-ai.onrender.com/v1/metadata
```

You should see JSON responses like:
```json
{"status":"ok","contexts_loaded":{"category":5,"customer":200,"merchant":50,"trigger":100},"uptime_seconds":0}
```

## Step 8: Submit to Challenge
1. Go to https://magicpin.com/vera/ai-challenge
2. **Public URL**: Paste your Render URL (e.g., `https://magicpin-vera-ai.onrender.com`)
3. **Upload Files**:
   - `submission.jsonl` (your 30 test messages)
   - `README.md` (your approach)
4. Click **"Submit"**

## Troubleshooting

### "Build failed"
- Check logs in Render dashboard
- Common issue: Missing `requirements.txt`
- Make sure `Procfile` has: `web: gunicorn app:app`

### "Module not found"
- Add to `requirements.txt`:
  ```
  flask
  gunicorn
  ```

### "Application failed to start"
- Test locally first: `python app.py`
- Check for syntax errors in `app.py`

### "Connection refused"
- Free tier sleeps after 15 min inactivity
- First request takes 10-20 seconds to wake up
- Just refresh and try again

## Your Files Are Ready
✅ `app.py` - Flask server with 5 endpoints
✅ `requirements.txt` - flask, gunicorn
✅ `Procfile` - web: gunicorn app:app
✅ `submission.jsonl` - 30 high-compulsion messages
✅ `README.md` - your approach documentation

**Follow these steps and you'll have a public URL in 10 minutes!** 🚀