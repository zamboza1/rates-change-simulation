# 🚀 Shipping the Full Stack App

We moved from Streamlit to a professional Full Stack architecture.
Here is how you ship it for free.

## 1. Backend (Render.com)

1.  Push code to GitHub.
2.  Sign up for **Render**.
3.  Create **New Web Service**.
4.  Connect GitHub repo.
5.  **Settings**:
    *   **Root Directory**: `.`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port 10000`
6.  Deploy. You will get a URL (e.g., `https://rates-change-simulation.onrender.com`).

## 2. Frontend (Vercel / GitHub Pages)

1.  Edit `frontend/index.html`.
2.  **CRITICAL**: Find `http://127.0.0.1:8000` and replace it with your Render Backend URL (`https://rates-change-simulation.onrender.com`).
3.  Deploy:
    *   **Vercel**: Import repo, set "Root Directory" to `frontend`.
    *   **GitHub Pages**: Push just the frontend folder or configure it to serve `frontend`.

## 3. Verify
Open your Vercel URL. You should see live rates flowing in from your Render backend.
