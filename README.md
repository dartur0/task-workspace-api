# Task & Team Workspace

A lightweight project management tool (Trello-style) with JWT authentication, built to practice designing a relational data model and securing a REST API.

## Features

- **JWT authentication** — registration, login, password hashing with bcrypt
- **Workspaces → Boards → Tasks** hierarchy with proper ownership checks on every write operation
- **Kanban-style board** — create tasks, move them between To Do / In Progress / Completed
- **Task priorities** (Low / Medium / High) with visual badges
- Minimal vanilla JS frontend served directly by FastAPI (no build step)

## Tech Stack

- **FastAPI** — REST API, dependency injection, auto-generated OpenAPI docs
- **SQLAlchemy** — ORM, relational schema with `One-to-Many` relationships
- **PostgreSQL** (SQLite fallback for local development without Docker)
- **JWT** (python-jose) + **bcrypt** for authentication
- **Docker / Docker Compose** — one-command setup with a Postgres container
- **Pytest** — integration tests for auth and workspace endpoints
- **Vanilla JavaScript (ES6)** — no framework on the frontend

## Data Model

```
User
 └── Workspace (owner_id)
      └── Board
           └── Task (assignee_id)
```

Every request that creates or modifies a `Board` or `Task` verifies that the resource belongs to the authenticated user before allowing the change.

## Running Locally

### With Docker (recommended)

```bash
docker compose up
```

The API will be available at `http://localhost:8000`, the UI at `http://localhost:8000/app`.

### Without Docker

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
SECRET_KEY=your-secret-key-here
```

Then start the server:

```bash
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/app` in your browser.

## API Documentation

FastAPI generates interactive API docs automatically:

```
http://127.0.0.1:8000/docs
```

## Running Tests

```bash
pytest
```

## Project Structure

```
.
├── main.py            # App entrypoint, router registration
├── database.py        # DB engine and session setup
├── models.py           # SQLAlchemy models
├── schemas.py          # Pydantic request/response schemas
├── security.py         # Password hashing, JWT creation/validation
├── auth.py             # Register / login / me endpoints
├── workspaces.py       # Workspace endpoints
├── tasks.py            # Board and task endpoints
├── static/             # Frontend (HTML/CSS/JS)
├── tests/               # Pytest integration tests
├── Dockerfile
└── docker-compose.yml
```

## License

MIT
