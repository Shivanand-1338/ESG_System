# Breathe ESG Data Ingestion System

A Django REST API with React frontend that consolidates emissions data from heterogeneous sources (SAP, Green Button, Concur), normalizes the data, detects quality issues, and provides an approval workflow for ESG analysts.

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL (optional, SQLite for development)

### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Access the Application

- **Backend API:** http://127.0.0.1:8000/api/v1/
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **Health Check:** http://127.0.0.1:8000/api/health/
- **Frontend (dev):** http://localhost:5173/

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login/` | Login and get token |
| POST | `/api/v1/auth/logout/` | Logout and delete token |
| GET | `/api/v1/auth/user/` | Get current user info |

### Data Ingestion
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ingest/sap/` | Ingest SAP data (IDoc/CSV) |
| POST | `/api/v1/ingest/greenbutton/` | Ingest Green Button XML |
| POST | `/api/v1/ingest/concur/` | Ingest Concur trip data |

### Data Retrieval
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/records/` | List records (paginated, filterable) |
| GET | `/api/v1/records/{id}/` | Get record details |
| GET | `/api/v1/records/suspicious/` | List flagged records |
| GET | `/api/v1/records/{id}/audit-trail/` | Get record audit trail |

### Approval Workflow
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/records/{id}/approve/` | Approve a record |
| POST | `/api/v1/records/bulk-approve/` | Bulk approve records |
| POST | `/api/v1/records/{id}/unapprove/` | Unapprove a record |
| POST | `/api/v1/records/{id}/dismiss-flag/` | Dismiss a flag |

### Statistics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/statistics/summary/` | Summary statistics |
| GET | `/api/v1/statistics/by-scope/` | Statistics by emission scope |

## Sample API Requests

```bash
# Login
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# List records
curl http://127.0.0.1:8000/api/v1/records/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "X-Tenant-ID: YOUR_TENANT_UUID"

# Approve a record
curl -X POST http://127.0.0.1:8000/api/v1/records/{id}/approve/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"justification": "Data verified"}'

# Get statistics
curl http://127.0.0.1:8000/api/v1/statistics/summary/ \
  -H "Authorization: Token YOUR_TOKEN"
```

## Architecture

```
Backend (Django REST Framework)
├── ingestion/          # Models, parsers, views, permissions
├── normalization/      # Unit converter, scope classifier, engine
├── breathe_esg/        # Django project settings
└── manage.py

Frontend (React + TypeScript + Vite)
├── src/
│   ├── components/     # UI components
│   ├── pages/          # Page components
│   ├── services/       # API service layer
│   └── types/          # TypeScript definitions
└── package.json
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | (generated) |
| `DEBUG` | Debug mode | `True` |
| `DATABASE_URL` | Database connection string | `sqlite:///db.sqlite3` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | CORS origins | `http://localhost:5173` |

## Deployment

The application is configured for deployment on cloud platforms (Render, Railway, Fly.io):

1. Set environment variables on the platform
2. Run `python manage.py migrate` on deploy
3. Build frontend: `cd frontend && npm run build`
4. Collect static files: `python manage.py collectstatic`
5. Start with Gunicorn: `gunicorn breathe_esg.wsgi`
