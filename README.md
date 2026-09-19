# PatentPulse

PatentPulse is a full-stack analytics platform for tracking and analyzing technology patent filings across key industry domains. It pairs a Django REST Framework backend with a Vue 3 single-page application to visualize filing volumes and citation dynamics over time, alongside a search and exploration table.

---

## Technology Stack

- **Backend:** Python 3.11+, Django 5+, Django REST Framework, django-filter, requests
- **Database:** SQLite (default for local development) or PostgreSQL
- **Frontend:** Vue 3 (Composition API), Vue Router, Chart.js, Axios, Vite
- **Testing:** Django `TestCase` and DRF `APITestCase` (14 automated unit and integration tests)
- **Containerization:** Docker & Docker Compose

---

## Project Structure

```
patentpulse/
├── backend/
│   ├── patentpulse/               # Django project configuration module
│   │   ├── __init__.py
│   │   ├── asgi.py                # ASGI entrypoint for asynchronous deployments
│   │   ├── settings.py            # Database, CORS, DRF, and app configurations
│   │   ├── urls.py                # Root URL router (mounts /api/ and /admin/)
│   │   └── wsgi.py                # WSGI entrypoint for web servers (e.g. Gunicorn)
│   ├── trends/                    # Core Django application
│   │   ├── management/commands/
│   │   │   ├── fetch_patents.py   # Live ingest from PatentsView Search API v1
│   │   │   └── seed_data.py       # Offline fixture loader for curated dataset
│   │   ├── migrations/            # Database schema migrations
│   │   ├── tests/                 # Test suite (models, APIs, management commands)
│   │   │   ├── test_api.py
│   │   │   ├── test_commands.py
│   │   │   └── test_models.py
│   │   ├── admin.py               # Django Admin registration
│   │   ├── apps.py                # App configuration (BigAutoField setup)
│   │   ├── models.py              # Patent model schema
│   │   ├── serializers.py         # DRF serializers (Patent & TrendPoint)
│   │   ├── urls.py                # Trends app URL routes
│   │   └── views.py               # ViewSets and aggregate analytics views
│   ├── data/
│   │   └── sample_patents.csv     # Bundled dataset (166 patents, 2018–2026)
│   ├── requirements.txt           # Python package dependencies
│   ├── manage.py                  # Django management script
│   └── Dockerfile                 # Backend container image definition
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   │   └── styles.css         # Dark theme UI styles
│   │   ├── components/
│   │   │   ├── SearchPanel.vue    # Domain, year range, and keyword search filters
│   │   │   └── TrendChart.vue     # Dual-axis Chart.js line visualization
│   │   ├── router/
│   │   │   └── index.js           # Vue Router routes (Dashboard & Explorer)
│   │   ├── services/
│   │   │   └── api.js             # Axios client for backend API communication
│   │   ├── views/
│   │   │   ├── Dashboard.vue      # Aggregate trends, stat cards, and timeline chart
│   │   │   └── Explorer.vue       # Filterable patent table with pagination
│   │   ├── App.vue                # Main application shell with navbar and footer
│   │   └── main.js                # Vue application bootstrapping
│   ├── index.html                 # Single-page application root HTML
│   ├── package.json               # Node.js dependencies and scripts
│   └── vite.config.js             # Vite configuration with API reverse proxy
├── docker-compose.yml             # PostgreSQL + Django orchestration
└── .gitignore                     # Git exclusion rules
```

---

## Dataset & Technology Domains

PatentPulse tracks patents across five technology domains:

1. **AI/ML** (CPC `G06N`): Neural architectures, transformers, diffusion models, LLM alignment, edge acceleration.
2. **Biotech** (CPC `A61K`, `C12N`): mRNA delivery, CRISPR/Cas systems, base editing, cell therapies, biosensors.
3. **Energy Storage** (CPC `H01M`): Solid-state electrolytes, silicon anodes, tabless cells, sodium-ion batteries, grid storage.
4. **IoT** (CPC `H04W`, `H04L`): LPWAN, UWB ranging, 5G/6G non-terrestrial networks, Matter protocol, energy harvesting.
5. **Cybersecurity** (CPC `H04L9`, `G06F21`): Post-quantum cryptography, zero-trust architectures, eBPF telemetry, homomorphic encryption.

The bundled dataset (`backend/data/sample_patents.csv`) contains **166 verified patent records** spanning **2018 through 2026** from leading corporate and academic assignees (Google, Tesla, Microsoft, Moderna, OpenAI, Qualcomm, Broad Institute, etc.).

---

## Quick Start (Local Setup)

### Prerequisites
- Python 3.11 or higher
- Node.js 18+ and npm

### 1. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
# Linux / macOS:
source venv/bin/activate
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Seed the database with the curated 2018-2026 patent dataset
python manage.py seed_data --clear

# Start the Django development server
python manage.py runserver 8000
```

The API will be live at `http://127.0.0.1:8000/api/`.

### 2. Frontend Setup

In a separate terminal window:

```bash
cd frontend

# Install dependencies
npm install

# Start the Vite development server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser. The Vite server automatically proxies `/api/*` requests to the Django backend on port 8000.

To compile a production frontend build:
```bash
npm run build
```

---

## Ingesting Live Data (PatentsView Search API)

The backend includes a management command to fetch live patent records directly from the PatentsView Search API v1 (`https://search.patentsview.org/api/v1/patent/`):

1. Obtain an API key from [PatentsView](https://search.patentsview.org/) or the [USPTO Open Data Portal](https://data.uspto.gov/).
2. Export the key to your environment:
   ```bash
   export PATENTSVIEW_API_KEY="your-api-key"
   # Windows PowerShell:
   $env:PATENTSVIEW_API_KEY="your-api-key"
   ```
3. Run the ingest command:
   ```bash
   python manage.py fetch_patents --clear --limit-per-domain 60
   ```
   **Flags:**
   - `--clear`: Empties the existing Patent table before loading fresh records.
   - `--limit-per-domain`: Maximum patents to fetch per domain (default: `60`).
   - `--page-size`: Number of records requested per API page (default: `50`).

*Note: For offline environments or local development, use `python manage.py seed_data --clear` to load the bundled dataset without an API key.*

---

## Running with Docker Compose

To launch a PostgreSQL database alongside the Django API:

```bash
docker compose up --build
```

The container automatically applies migrations and loads the seed dataset on startup. Run the frontend development server separately (`cd frontend && npm run dev`).

---

## Running the Automated Test Suite

```bash
cd backend
python manage.py test
```

Runs 14 automated tests covering:
- **Models:** String representation, default ordering by year and citation count.
- **REST APIs:** List, domain filtering, year range filtering, multi-field keyword search.
- **Analytics:** Multi-year domain aggregation, citation coalescing, distinct domain listing.
- **Management Commands:** Offline fixture loading (`seed_data`), PatentsView API client mocking, API key validation, and `--clear` flag behavior.

---

## REST API Reference

All API routes are served under `/api/`:

| Method | Endpoint | Query Parameters | Description |
|---|---|---|---|
| `GET` | `/api/patents/` | `domain`, `year`, `year_from`, `year_to`, `search`, `page` | Returns a paginated list of patents (25 per page) matching filter criteria. |
| `GET` | `/api/trends/summary/` | `domain` (optional) | Returns aggregated filing counts and citation totals grouped by `filing_year` and `technology_domain`. |
| `GET` | `/api/trends/domains/` | *None* | Returns a sorted list of unique technology domain names currently stored. |
| `GET` | `/admin/` | *None* | Django administrative interface for inspecting and editing patent records. |

### Example Query

```bash
# Retrieve patents in AI/ML filed between 2022 and 2026 containing "transformer"
curl "http://127.0.0.1:8000/api/patents/?domain=AI/ML&year_from=2022&year_to=2026&search=transformer"
```
