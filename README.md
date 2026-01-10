# Project Tools API

![CI](https://github.com/marcin119a/project_tools/actions/workflows/ci.yml/badge.svg)

API for managing real estate listings and locations built with FastAPI, SQLAlchemy, and SQLite.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Database](#database)
- [Data Import](#data-import)
- [Testing](#testing)
- [Development](#development)

## ✨ Features

- **RESTful API** built with FastAPI
- **Asynchronous database operations** using SQLAlchemy 2.0 with async support
- **SQLite database** with Alembic migrations
- **Data validation** with Pydantic v2
- **Health check endpoint** for monitoring
- **CSV data import** functionality for real estate listings
- **Comprehensive test suite** using pytest
- **API documentation** with automatic Swagger UI and ReDoc

## 🛠 Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: SQLite with aiosqlite
- **ORM**: SQLAlchemy 2.0 (async)
- **Validation**: Pydantic v2
- **Migrations**: Alembic
- **Testing**: pytest with pytest-asyncio
- **Server**: Uvicorn

## 📦 Requirements

- Python 3.8+
- pip

## 🚀 Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd project_tools
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

The application uses SQLite by default with the following configuration:

- **Database URL**: `sqlite+aiosqlite:///./sql_app.db`
- **Database file**: `sql_app.db` (created automatically in project root)

### Database Configuration

The database configuration is located in `models/database.py`:
- Async engine with `check_same_thread=False` for SQLite
- Echo mode enabled for SQL query logging (can be disabled in production)

## 🏃 Running the Application

### Development Mode

Using the new FastAPI CLI (recommended):
```bash
fastapi dev main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

### Production Mode

```bash
fastapi run
```

Or with uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📁 Project Structure

```
project_tools/
├── alembic/                    # Database migrations
│   ├── versions/               # Migration files
│   └── env.py                  # Alembic environment config
├── data/                       # Data files
│   └── ogloszenia_warszawa_detailed.csv
├── models/                     # SQLAlchemy models
│   ├── base.py                 # Base model class
│   ├── database.py             # Database connection and session
│   └── models.py               # Data models (Location, Building, Owner, Features, Listing)
├── routers/                    # API route handlers
│   ├── health.py               # Health check endpoint
│   └── hello.py                # Hello world endpoints
├── schemas/                    # Pydantic schemas
│   ├── health.py               # Health check response schemas
│   └── hello.py                # Hello response schemas
├── tests/                      # Test suite
│   ├── conftest.py             # pytest configuration and fixtures
│   └── test_health.py          # Health endpoint tests
├── alembic.ini                 # Alembic configuration
├── import_listings.py          # CSV import script
├── main.py                     # FastAPI application entry point
├── pytest.ini                  # pytest configuration
└── requirements.txt            # Python dependencies
```

## 🔌 API Endpoints

### Root
- **GET /** - API information and available endpoints

### Health Check
- **GET /health/** - Check API and database health status

### Hello
- **GET /hello** - Returns "Hello World" message
- **GET /hello/{name}** - Returns personalized greeting

### Documentation
- **GET /docs** - Interactive API documentation (Swagger UI)
- **GET /redoc** - Alternative API documentation (ReDoc)

## 🗄 Database

### Database Models

The application uses the following database models:

1. **Location** - Geographic information
   - city, locality, city_district, street
   - full_address, latitude, longitude

2. **Building** - Building details
   - year_built, building_type, floor

3. **Owner** - Owner information
   - owner_type, contact details

4. **Features** - Property features
   - has_basement, has_parking
   - kitchen_type, window_type
   - ownership_type, equipment

5. **Listing** - Real estate listings
   - rooms, area, price information
   - date_posted, photo_count
   - url, image_url, description
   - Foreign keys to Location, Building, Owner, Features

### Migrations

The project uses Alembic for database migrations.

**Create a new migration**:
```bash
alembic revision --autogenerate -m "Description of changes"
```

**Apply migrations**:
```bash
alembic upgrade head
```

**Rollback migrations**:
```bash
alembic downgrade -1
```

**View migration history**:
```bash
alembic history
```

### Database Initialization

The database tables are automatically created on application startup using the lifespan context manager in `main.py`.

## 📥 Data Import

The project includes a script to import real estate listings from CSV files.

**Run the import script**:
```bash
python import_listings.py
```

The script:
- Reads data from `data/ogloszenia_warszawa_detailed.csv`
- Cleans and validates all data
- Creates or updates Location, Building, Owner, and Features records
- Imports listings with proper relationships
- Handles duplicates and data integrity

### Import Features

- Data cleaning and validation
- Decimal and integer parsing
- Date parsing with multiple formats
- Boolean field conversion
- Duplicate detection based on URL
- Transaction-based processing for data integrity
- Detailed logging of import process

## 🧪 Testing

The project uses pytest with async support for testing.

**Run all tests**:
```bash
pytest
```

**Run with verbose output**:
```bash
pytest -v
```

**Run specific test file**:
```bash
pytest tests/test_health.py
```

**Run with coverage**:
```bash
pytest --cov=.
```

### Test Configuration

- Test configuration in `pytest.ini`
- Fixtures and test database setup in `tests/conftest.py`
- Async test support via `pytest-asyncio`

## 👨‍💻 Development

### Code Style

The project follows these conventions:
- **Async operations**: Use `async def` for all database operations
- **Type hints**: All functions have type annotations
- **Dependency Injection**: Use `Annotated` with FastAPI `Depends`
- **Response models**: All endpoints have defined `response_model`
- **File naming**: Lowercase with underscores (snake_case)
- **Comments**: Written in English

### Adding New Endpoints

1. Create a Pydantic schema in `schemas/`
2. Create a router in `routers/`
3. Include the router in `main.py`
4. Add tests in `tests/`

### Adding New Models

1. Define SQLAlchemy model in `models/models.py`
2. Create migration: `alembic revision --autogenerate -m "Add model"`
3. Apply migration: `alembic upgrade head`
4. Create corresponding Pydantic schemas in `schemas/`

## 📝 Environment Variables

Currently, the application uses default configuration. For production, consider adding:

- `DATABASE_URL` - Custom database connection string
- `DEBUG` - Debug mode toggle
- `LOG_LEVEL` - Logging level configuration

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

[Add your license information here]

## 👥 Authors

[Add author information here]

---

**API Version**: 1.0.0

For more information, visit the [interactive API documentation](http://localhost:8000/docs) after starting the server.

