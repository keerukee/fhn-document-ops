# FHN Document Ops - Architectural Flows

To avoid creating a massive, confusing diagram, it is highly recommended to split the architecture into **three distinct flows** when prompting Lucidchart AI.

Here are the detailed, step-by-step descriptions for each flow. You can copy and paste these directly into Lucidchart AI.

---

## Flow 1: Internal Request Generation (The Setup)
**Purpose**: How the internal bank application sets up a secure upload request for a customer.

**Actors & Systems**: 
- Internal Bank App
- FHN FastAPI Backend
- PostgreSQL Database

**Sequence of Events**:
1. The **Internal Bank App** sends a POST request (JSON containing customer details and a list of requested document types) to the **FHN FastAPI Backend** (`/api/v1/internal/requests/structured`). This endpoint is secured via JWT authentication.
2. The **FHN FastAPI Backend** receives the request and generates a unique GUID for the `UploadRequest`.
3. The **FHN FastAPI Backend** writes the `UploadRequest` and child `ExpectedDocument` records to the **PostgreSQL Database** with a status of `PENDING`.
4. The **FHN FastAPI Backend** generates a secure, temporary frontend URL containing the GUID.
5. The **FHN FastAPI Backend** returns the frontend URL to the **Internal Bank App**.
6. The **Internal Bank App** provides this link to the Customer (via email/SMS).

---

## Flow 2: Customer Document Upload (The Public Flow)
**Purpose**: How the customer securely uploads their documents (including partial uploads and extra documents).

**Actors & Systems**: 
- Customer (Web Browser)
- FHN React SPA (Frontend)
- FHN FastAPI Backend
- Azure Blob Storage
- Redis (Celery Broker)
- PostgreSQL Database

**Sequence of Events**:
1. The **Customer** clicks the link and opens the **FHN React SPA**.
2. The **FHN React SPA** fetches the list of required documents from the **FHN FastAPI Backend** (`GET /api/v1/public/requests/{id}`).
3. The **Customer** drags and drops their files into the UI and clicks "Submit Documents".
4. The **FHN React SPA** sends a multipart/form-data POST request to the **FHN FastAPI Backend** (`/api/v1/public/requests/{id}/upload`).
5. The **FHN FastAPI Backend** streams the files directly into **Azure Blob Storage**.
6. **Azure Blob Storage** returns the persistent `blob_url` for each file.
7. The **FHN FastAPI Backend** updates the corresponding `ExpectedDocument` statuses in the **PostgreSQL Database** to `UPLOADED` and saves the `blob_url`. (If it's an unlisted extra document, it creates a new `ExpectedDocument` row dynamically).
8. The **FHN FastAPI Backend** pushes an async task payload (containing `request_id`, `document_id`, and `blob_url`) to **Redis** (the Celery message broker).
9. The **FHN FastAPI Backend** responds with a success message to the **FHN React SPA**.

---

## Flow 3: Async Validation & Messaging (The Background Flow)
**Purpose**: How documents are processed with AI and how events are broadcasted back to the bank.

**Actors & Systems**: 
- Celery Worker (Python Background Process)
- Azure Document Intelligence (OCR)
- Azure Foundry (NLP Validation)
- PostgreSQL Database
- Kafka Message Broker
- Internal Bank App (Kafka Consumer)

**Sequence of Events**:
1. The **Celery Worker** continuously listens to Redis and picks up the new document task.
2. The **Celery Worker** passes the document URL to **Azure Document Intelligence** to extract raw text and key-value pairs (OCR).
3. The **Celery Worker** sends the extracted data to **Azure Foundry** to evaluate it against business rules and determine a validation confidence score.
4. The **Celery Worker** updates the `ExpectedDocument` in the **PostgreSQL Database** to `VALIDATED` or `FAILED`.
5. The **Celery Worker** publishes a `FILE_PROCESSED` event to the **Kafka Message Broker**. This JSON payload includes the `blob_url` and `validation_results` so the internal app gets it instantly, regardless of validation success.
6. The **Celery Worker** queries the **PostgreSQL Database** to check if all expected documents for this request are now fully processed. 
7. If all documents are fully processed AND the overall request status is locked as `COMPLETED` (triggered by the user clicking "Finish & Lock Request" in Flow 2), the **Celery Worker** publishes a final `REQUEST_COMPLETED` event to the **Kafka Message Broker**.
8. The **Internal Bank App** consumes these Kafka events to update its internal dashboards and workflow state.
