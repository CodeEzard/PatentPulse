# PatentPulse

PatentPulse is a full-stack technology intelligence and patent analytics platform. It monitors filing velocity, citation momentum, and cross-domain innovation trajectories across emerging technology sectors. Built with a Django REST Framework backend and a Vue 3 dashboard powered by Chart.js.

- **Live Application:** [patent-pulse-sigma.vercel.app](https://patent-pulse-sigma.vercel.app)
- **API Endpoint:** [patentpulse-backend.onrender.com](https://patentpulse-backend.onrender.com)

---

## Key Features

- **Trend Analytics Dashboard:** Annual filing counts and citation volume trajectories with customizable metric toggles (Filings, Citations, or Both) and domain filtering.
- **Patent Explorer:** Filterable search interface with keyword tagging, domain classification badges, citation impact indicators, and direct links to Google Patents documents.
- **Sector Comparison Matrix:** High-level domain performance cards with one-click drilldown into sector trends.
- **Efficient Aggregations:** Database-level grouping using Django ORM annotations (`Count`, `Sum`, `Coalesce`) for fast queries over time-series data.
- **Curated Dataset & Live Ingestion:** Pre-seeded with 166 verified patent publications spanning 2018 through 2026, alongside an automated ingestion pipeline for the USPTO / PatentsView API.
- **Modern Responsive Dark Theme:** Custom design system built with CSS variables, ambient radial glow, domain color coding, and animated skeleton loaders.

---

## Technology Stack

- **Backend:** Python 3.11, Django 5, Django REST Framework, django-filter, django-cors-headers, Gunicorn
- **Database:** SQLite (default for development) or PostgreSQL
- **Frontend:** Vue 3 (Composition API), Vite, Vue Router 4, Chart.js, Axios
- **Testing:** Django `TestCase` and DRF `APITestCase` (15 unit and integration tests)
- **Containerization:** Docker & Docker Compose

---

## Repository Structure

```
patentpulse/
├── backend/
│   ├── patentpulse/          # Django configuration, settings, root URL router
│   ├── trends/               # Data models, analytics views, serializers, tests
│   │   ├── management/       # Data ingestion & fixture seeding commands
│   │   ├── migrations/       # Schema migrations
│   │   └── tests/            # Automated test suite (API, models, commands)
│   ├── data/                 # Curated patent dataset (2018–2026)
│   ├── manage.py
│   ├── requirements.txt
│   ├── build.sh              # Production build script (Render)
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       # TrendChart, SearchPanel
│   │   ├── views/            # Dashboard, Explorer
│   │   ├── services/         # Axios API client
│   │   ├── assets/           # Design system tokens and styles
│   │   └── App.vue           # Main application shell & navigation
│   ├── package.json
│   └── vite.config.js
└── docker-compose.yml         # Local multi-container orchestration
```

---

## Technology Domains

The platform tracks patent publications across five technology domains:

| Domain | CPC Classification | Focus Areas |
|---|---|---|
| **AI / Machine Learning** | `G06N` | Transformers, neural accelerators, diffusion models, LLM alignment, federated learning |
| **Biotechnology** | `A61K`, `C12N` | mRNA delivery, CRISPR/Cas gene editing, base editing, targeted therapeutics |
| **Energy Storage** | `H01M` | Solid-state electrolytes, silicon anodes, tabless cells, sodium-ion chemistry |
| **Internet of Things** | `H04W`, `H04L` | Ultra-wideband ranging, LPWAN mesh networks, 5G/6G NTN, edge telemetry |
| **Cybersecurity** | `H04L9`, `G06F21` | Post-quantum lattice cryptography, zero-trust architectures, confidential computing |

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 1. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations and seed data
python manage.py migrate
python manage.py seed_data --clear

# Start the development server
python manage.py runserver 8000
```

The API will be available at `http://127.0.0.1:8000/`.

### 2. Frontend Setup

In a separate terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start the Vite development server
npm run dev
```

Visit [http://localhost:5173](http://localhost:5173) in your browser. Vite proxies `/api/*` requests directly to the Django server.

To create a production build:
```bash
npm run build
```

---

## Running with Docker Compose

To run the backend with a PostgreSQL database in Docker:

```bash
docker compose up --build
```

The service runs migrations, seeds the database, and exposes the API on port `8000`.

---

## Ingesting Live USPTO Data

To fetch live patents directly from the PatentsView / USPTO Search API:

```bash
# Set your API key
export PATENTSVIEW_API_KEY="your-api-key"
# Windows PowerShell: $env:PATENTSVIEW_API_KEY="your-api-key"

# Ingest records
python manage.py fetch_patents --clear --limit-per-domain 50
```

*For local testing, `python manage.py seed_data --clear` loads the bundled dataset without requiring an API key.*

---

## Running Automated Tests

```bash
cd backend
python manage.py test
```

Runs 15 automated test cases covering:
- **Models:** Default ordering by year and citation count, string representation.
- **REST APIs:** Filtering by domain, year range, keyword search, and Google Patents URL resolution.
- **Aggregations:** Multi-year trend grouping, citation coalescing, distinct domain listing.
- **Management Commands:** Fixture loading, PatentsView API mocking, and error handling.

---

## REST API Reference

| Method | Endpoint | Query Parameters | Description |
|---|---|---|---|
| `GET` | `/` | *None* | Root health check and available endpoints list |
| `GET` | `/api/patents/` | `domain`, `year_from`, `year_to`, `search`, `page` | Paginated list of patents (25 per page) with Google Patents reference links |
| `GET` | `/api/trends/summary/` | `domain` (optional) | Aggregated filing counts and citation totals grouped by year and domain |
| `GET` | `/api/trends/domains/` | *None* | Sorted list of unique technology domains |
| `GET` | `/admin/` | *None* | Django administration portal |

### Example Query

```bash
# Retrieve AI/ML patents filed between 2022 and 2026 containing "transformer"
curl "http://127.0.0.1:8000/api/patents/?domain=AI/ML&year_from=2022&year_to=2026&search=transformer"
```
