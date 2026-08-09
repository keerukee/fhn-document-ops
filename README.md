# First Horizon Document Operations (FHN-Document-Ops)

## Architectural Flow
The application provides a secure mechanism for First Horizon customers to upload requested documents via a temporary link.
1. **Request Creation**: An internal bank application hits the `POST /api/v1/internal/requests` endpoint (structured or unstructured) to generate an upload link for a specific customer.
2. **Customer Portal**: The customer navigates to the React single-page application using the provided link. They see the requested documents and drag-and-drop their files into the UI.
3. **Upload & Storage**: The frontend submits the files to the Python FastAPI backend, which streams the files securely to **Azure Blob Storage**.
4. **Asynchronous Processing**: A **Celery Worker** picks up the uploaded document in the background:
   - Calls **Azure Document Intelligence** to extract OCR data.
   - Forwards the extracted data to **Azure Foundry** for NLP-based validation against predefined rules.
5. **Messaging**: Regardless of validation success or failure, a final event is published to a **Kafka Topic**, notifying the internal bank application that the customer has submitted the documents and providing the validation results.

## Codebase Structure
The repository is split into two independent projects for modularity:
- `/frontend`: React 18, TypeScript, and Vite. Styled with Tailwind CSS v4 using First Horizon brand themes.
- `/backend`: Python FastAPI application built using Domain-Driven Design (DDD).

### Backend Component Breakdown (DDD)
- `api/routers`: FastAPI route handlers (separated into `internal.py` and `public.py`).
- `core`: Security (JWT) and Configuration management.
- `models`: SQLAlchemy Async ORM models defining the database tables (`UploadRequest`, `ExpectedDocument`).
- `schemas`: Pydantic models for incoming payload validation and response serialization.
- `services`: Business logic "bricks" that wrap external integrations (StorageService, AIService, ValidationService, MessagingService, RequestService).
- `workers`: Celery background tasks.

## Configuration Guide
The application relies heavily on environment variables, loaded via `.env` in the backend. 

We support a **Mock Mode** for local development when network access to Azure or the Database is unavailable.

### Setting up `.env`
Create a `.env` file inside the `/backend` directory based on the `/backend/.env.example` file.
```env
# Example of Mock Mode Config for Local Network
USE_MOCK_DB=True
USE_MOCK_STORAGE=True
```
- When `USE_MOCK_DB=True`, PostgreSQL is bypassed and a local SQLite file (`fhn_mock.db`) is used.
- When `USE_MOCK_STORAGE=True`, network calls to Azure Blob Storage are bypassed, and a simulated URL is returned.

### External Integration Variables
When deploying to production or an environment with access, set mock modes to `False` and supply:
- `DATABASE_URL`
- `AZURE_STORAGE_CONNECTION_STRING`
- `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` & `KEY`
- `AZURE_FOUNDRY_URL`
- `KAFKA_BOOTSTRAP_SERVERS`

## Local Development Guide

### 1. Running the Frontend
```bash
cd frontend
npm install
npm run dev
```

### 2. Running the Backend API
```bash
cd backend
python -m venv venv
# On Windows: .\venv\Scripts\Activate.ps1
# On Mac/Linux: source venv/bin/activate
pip install -r requirements.txt # (Ensure dependencies are installed)
uvicorn app.main:app --reload
```

### 3. Running the Celery Worker
Make sure Redis is running locally (`redis-server`), then:
```bash
cd backend
celery -A app.workers.tasks worker --loglevel=info
```
