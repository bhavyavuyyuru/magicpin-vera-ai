# Deployment Options for Magicpin AI Challenge

## Option 1: Deploy to Heroku (Free Tier Alternative)
- Sign up at https://www.heroku.com/
- Create a new app
- Push your code: `git init`, `git add .`, `git commit -m "Initial"`, `heroku create`, `git push heroku main`
- Your public URL: `https://your-app-name.herokuapp.com`

## Option 2: Deploy to Render.com
- Sign up at https://render.com
- Connect GitHub repo
- Create new Web Service
- Set start command: `python app.py`
- Your public URL: `https://your-app-name.onrender.com`

## Option 3: Deploy to Railway.app
- Sign up at https://railway.app
- Connect GitHub
- Deploy
- Your public URL: `https://your-app-name.railway.app`

## Option 4: Deploy to PythonAnywhere
- Sign up at https://www.pythonanywhere.com/
- Upload code
- Set up Web app with Flask
- Your public URL: `https://yourusername.pythonanywhere.com`

## Deployment Files Needed

Create `Procfile` for hosting platforms:
```
web: gunicorn app:app
```

Create `requirements.txt`:
```
flask
gunicorn
```

## How to Test Your Public URL

Once deployed, test with:
```bash
curl -X GET https://your-public-url/v1/healthz
curl -X GET https://your-public-url/v1/metadata
```

## For Challenge Submission

1. Deploy `app.py` to a public URL
2. Submit the URL: `https://your-deployment-url.com`
3. Ensure endpoints are working:
   - `GET /v1/healthz` → returns status
   - `GET /v1/metadata` → returns team info
   - `POST /v1/context` → accepts context
   - `POST /v1/tick` → returns actions
   - `POST /v1/reply` → handles replies

The judge will call your public URL endpoints during evaluation.