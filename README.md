# FastAPI Vercel Wrapper

Is project ko direct Vercel par deploy karne ke liye niche diye steps follow karein:

## Deployment on Vercel
1. Iss ZIP ko extract karke GitHub repo par push karein.
2. Vercel dashboard par `Import Repository` select karein.
3. Vercel `vercel.json` and `api/index.py` ko automatic build kar lega.

## Local Running
```bash
pip install -r requirements.txt
uvicorn api.index:app --reload
```
Open `http://127.0.0.1:8000/docs` for Interactive Swagger API Docs.
