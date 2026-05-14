# AI Travel Assistant

Vue 3 + FastAPI full-stack AI travel assistant demo.

## Run Locally

Backend:

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

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
