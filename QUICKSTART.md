# DevSEO Quick Start Guide

This guide will help you get DevSEO running locally in just a few minutes.

## Prerequisites

Make sure you have the following installed:
- **Node.js 18+** and npm
- **Python 3.12+**
- **Docker Desktop** (for PostgreSQL and Redis)

## Step-by-Step Setup

### 1. Start Database Services

Open a terminal and navigate to the project directory:

```bash
cd C:\Users\User\devseo
docker-compose up -d
```

This will start:
- PostgreSQL on port 5432
- Redis on port 6379

Verify services are running:
```bash
docker-compose ps
```

### 2. Set Up Backend

Open a new terminal window:

```bash
cd C:\Users\User\devseo\backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the backend server
python -m app.main
```

The backend API will be running at: **http://localhost:8000**

API documentation available at: **http://localhost:8000/docs**

### 3. Set Up Frontend

Open another new terminal window:

```bash
cd C:\Users\User\devseo\frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be running at: **http://localhost:3000**

## Test the Application

### 1. Register a New Account

1. Open your browser and go to: http://localhost:3000
2. You'll be redirected to the login page
3. Click "Sign up" to go to the registration page
4. Fill in the form:
   - **Name**: Your Name (optional)
   - **Email**: test@example.com
   - **Password**: TestPass123 (must have uppercase, lowercase, and digit)
   - **Confirm Password**: TestPass123
5. Click "Create Account"

You should be automatically logged in and redirected to the dashboard!

### 2. Explore the Dashboard

After logging in, you'll see:
- **Dashboard Overview**: Welcome message and stats (currently showing 0 websites)
- **Sidebar Navigation**: Dashboard, Websites, Reports, Keywords, Settings
- **Getting Started Guide**: Step-by-step instructions

### 3. Test the API (Optional)

You can also test the API directly using the Swagger UI:

1. Go to: http://localhost:8000/docs
2. Try the `/api/v1/health` endpoint to verify the API is running
3. Use the `/api/v1/auth/register` endpoint to create a user via API
4. Use the `/api/v1/auth/login` endpoint to get JWT tokens

## What's Next?

Now that you have the foundation running, you can:

1. **Implement Website CRUD** - Add, list, and manage websites
2. **Build the Crawler** - Create the web crawler service
3. **Add SEO Analysis** - Implement the SEO scoring engine
4. **Integrate Claude API** - Add AI-powered content suggestions
5. **Set up Celery** - Configure background job processing

Refer to [README.md](README.md) for the full feature roadmap and architecture details.

## Troubleshooting

### Database Connection Error

If you see a database connection error:
1. Make sure Docker containers are running: `docker-compose ps`
2. Check if PostgreSQL is accessible: `docker-compose logs postgres`
3. Verify the DATABASE_URL in `backend/.env`

### Frontend Build Errors

If you encounter TypeScript errors:
1. Delete `node_modules` and `package-lock.json`
2. Run `npm install` again
3. Restart the dev server

### Port Already in Use

If port 8000 or 3000 is already in use:
- **Backend**: Change the port in `backend/app/main.py` (line with `uvicorn.run`)
- **Frontend**: Run `npm run dev -- -p 3001` to use port 3001

### Module Not Found Errors

Backend:
```bash
cd backend
pip install -r requirements.txt
```

Frontend:
```bash
cd frontend
npm install
```

## Useful Commands

### Backend

```bash
# Start backend
python -m app.main

# Run with auto-reload
uvicorn app.main:app --reload

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Run tests (once implemented)
pytest
```

### Frontend

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### Docker

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart postgres
```

## Project Structure

```
devseo/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── models/    # Database models
│   │   ├── routers/   # API endpoints
│   │   ├── schemas/   # Pydantic schemas
│   │   └── main.py    # FastAPI app
│   └── alembic/       # Database migrations
├── frontend/          # Next.js frontend
│   ├── app/           # Pages and layouts
│   ├── components/    # React components
│   └── lib/           # Utilities and API client
└── docker-compose.yml # Docker services
```

## Need Help?

- Check the main [README.md](README.md) for detailed documentation
- Review the API docs at http://localhost:8000/docs
- Look at the code comments for implementation details

Happy coding! 🚀
