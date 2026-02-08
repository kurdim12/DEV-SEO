# DevSEO - AI-Powered SEO Analysis Platform

DevSEO is a comprehensive SEO analysis SaaS platform tailored for developers, technical professionals, and small agencies with a focus on the MENA region. The platform crawls user websites, performs technical SEO audits, provides AI-driven content optimization suggestions, and tracks keyword rankings over time.

## Tech Stack

### Backend
- **FastAPI** - Async REST API framework
- **PostgreSQL** - Primary database (via SQLAlchemy + Alembic)
- **Redis** - Caching, rate limiting, and Celery broker
- **Celery** - Background job queue for crawling & report generation
- **Anthropic Claude API** - AI-powered content optimization
- **Stripe** - Subscription billing
- **SendGrid** - Transactional emails

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Strict mode
- **Tailwind CSS + shadcn/ui** - Styling and component library
- **NextAuth.js** - Authentication
- **Recharts** - Data visualization

## Getting Started

### Prerequisites
- Node.js 18+ (for frontend)
- Python 3.12+ (for backend)
- Docker & Docker Compose (for local development)
- PostgreSQL 16
- Redis 7

### Local Development Setup

#### 1. Clone the repository
```bash
git clone <repository-url>
cd devseo
```

#### 2. Start Docker services (PostgreSQL + Redis)
```bash
docker-compose up -d postgres redis
```

#### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env and fill in required values

# Run database migrations
alembic upgrade head

# Start backend server
python -m app.main
# or
uvicorn app.main:app --reload
```

The backend API will be available at http://localhost:8000

API documentation: http://localhost:8000/docs

#### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local
# Edit .env.local and fill in required values

# Start development server
npm run dev
```

The frontend will be available at http://localhost:3000

### Environment Variables

#### Backend (.env)
See `backend/.env.example` for all available variables. Required variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - Application secret key
- `JWT_SECRET` - JWT signing secret

#### Frontend (.env.local)
See `frontend/.env.example` for all available variables. Required variables:
- `NEXT_PUBLIC_API_URL` - Backend API URL
- `NEXTAUTH_URL` - Frontend URL
- `NEXTAUTH_SECRET` - NextAuth secret

### Database Migrations

Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## Project Structure

```
devseo/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── routers/         # API route handlers
│   │   ├── services/        # Business logic layer
│   │   ├── workers/         # Celery background tasks
│   │   ├── middleware/      # Custom middleware
│   │   ├── utils/           # Utility functions
│   │   ├── config.py        # Application settings
│   │   ├── database.py      # Database connection
│   │   ├── dependencies.py  # FastAPI dependencies
│   │   └── main.py          # FastAPI app initialization
│   ├── alembic/             # Database migrations
│   ├── tests/               # pytest test suite
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── app/                 # Next.js app directory
│   │   ├── (auth)/          # Authentication pages
│   │   ├── (dashboard)/     # Dashboard pages
│   │   └── api/             # API routes
│   ├── components/          # React components
│   │   ├── ui/              # shadcn/ui components
│   │   ├── dashboard/       # Dashboard-specific components
│   │   └── shared/          # Shared components
│   ├── lib/                 # Utility functions
│   ├── hooks/               # Custom React hooks
│   ├── types/               # TypeScript types
│   └── package.json         # Node dependencies
└── docker-compose.yml       # Docker services configuration
```

## Features (MVP Phase 1)

### Sprint 1-2: Foundation & Core Crawling
- [x] User authentication (register, login, JWT)
- [x] Dashboard with sidebar navigation
- [ ] Website CRUD operations
- [ ] Domain verification (DNS TXT record)
- [ ] Web crawler with robots.txt compliance
- [ ] SEO analyzer with technical checks
- [ ] Background job processing with Celery

### Sprint 3: AI & Keywords
- [ ] Claude API integration for content suggestions
- [ ] Keyword tracking setup
- [ ] Keyword ranking history
- [ ] Stripe subscription management
- [ ] Plan enforcement

### Sprint 4: Polish & Launch
- [ ] Email notifications
- [ ] PDF report export
- [ ] Landing page + pricing page
- [ ] Onboarding flow
- [ ] Arabic language support (i18n)
- [ ] Error tracking (Sentry)
- [ ] Analytics (PostHog)

## Development Guidelines

### Code Quality
- Python: Type hints on all functions, ruff for linting
- TypeScript: Strict mode, ESLint + Prettier
- Write tests for all services (pytest + pytest-asyncio)
- Use conventional commits

### Security
- Hash passwords with bcrypt (12 rounds)
- Validate all inputs with Pydantic (backend) and Zod (frontend)
- Never render raw HTML from crawled sites
- Rate limit all API endpoints
- Store secrets in environment variables

### Crawling Ethics
- Always respect robots.txt
- Max 2 requests/second per domain
- Proper User-Agent identification
- Don't crawl login-protected pages
- Implement exponential backoff on errors

## License

Proprietary - All rights reserved

## Support

For issues and questions, please contact the development team.
