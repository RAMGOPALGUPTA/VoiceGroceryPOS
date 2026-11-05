## Backend setup (Windows PowerShell)

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Run API: `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`

Open http://127.0.0.1:8000/docs. The M1 backend currently exposes health and basic product list/create/read endpoints. Database migration and seed scripts are next; no voice or checkout logic is implemented yet.
