# AI Travel Assistant

Vue 3 + FastAPI full-stack AI travel assistant demo.

## Run Locally

One-click startup on Windows:

```powershell
.\start-dev.ps1
```

Or double-click `start-dev.bat`.

The script clears old processes on ports `8000` and `5173`, then starts the FastAPI backend and Vite frontend together.

Backend:

```bash
cd backend
python -m pip install -r requirements.txt
copy ..\.env.example .env
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `backend/.env` and replace `OPENAI_API_KEY=your_api_key_here` with your own key.
The backend uses an OpenAI-compatible chat-completions endpoint. You can also change
`OPENAI_BASE_URL` and `OPENAI_MODEL` if your provider supports the same API shape.
If no key is configured, chat and itinerary planning keep using the local fallback demo.

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

## Demo Flow

1. Open `/auth` and register a user.
2. Go to `/trips`.
3. Submit the default Hangzhou trip form.
4. The frontend calls `POST /api/trips/plan-async`.
5. The frontend polls `GET /api/tasks/{task_id}` and renders the itinerary result.

## Verification

Backend:

```bash
cd backend
python -m pytest
```

Frontend:

```bash
cd frontend
npm run build
```
