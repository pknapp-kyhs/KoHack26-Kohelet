# KoHack26-Kohelet
Backend

## Files Overview

### Root Level
- [README.md](README.md) - Project documentation and overview.
- [requirements.txt](requirements.txt) - Python dependencies and package versions.
- [DEPENDENCIES_GUIDE.md](DEPENDENCIES_GUIDE.md) - Detailed explanation of all libraries and their purposes.

### Backend Directory (`backend/`)
- [backend/main.py](backend/main.py) - FastAPI application entry point with all API endpoints and core server logic.
- [backend/auth.py](backend/auth.py) - Authentication functions including JWT token creation/verification and password hashing.
- [backend/database.py](backend/database.py) - Database configuration and session management using SQLAlchemy.
- [backend/models.py](backend/models.py) - SQLAlchemy ORM models defining database tables for users, tasks, and checklist items.
- [backend/schemas.py](backend/schemas.py) - Pydantic schemas for request/response validation and serialization.

### Backend Scripts (`backend/scripts/`)
- [backend/scripts/patch_frontend_auth.py](backend/scripts/patch_frontend_auth.py) - Utility script for patching frontend authentication configuration.

### Documentation (`docs/`)
- [docs/technical_design_spec.md](docs/technical_design_spec.md) - Technical specification and system design documentation.
- [docs/coding guidelines.md](docs/coding%20guidelines.md) - Code style and best practices for the project.
- [docs/coding rubric.txt](docs/coding%20rubric.txt) - Rubric for evaluating code quality.
- [docs/project framework goals.txt](docs/project%20framework%20goals.txt) - High-level project objectives and goals.
- [docs/Code Complexity Rubric](docs/Code%20Complexity%20Rubric) - Rubric for assessing code complexity.

### Frontend (`frontend/`)
- [frontend/index.html](frontend/index.html) - Single-page application with HTML, CSS, and JavaScript for the user interface.

## Features

1. **User Gamification** - Users can register, log in, and track their progress through streaks, XP points, and level progression (implemented in [backend/auth.py](backend/auth.py) and [backend/models.py](backend/models.py)).

2. **Mitzvah Tracking & Task Management** - Users can track daily Jewish religious tasks and practices, with difficulty tiers and time estimates (core logic in [backend/main.py](backend/main.py) with database models in [backend/models.py](backend/models.py)).

3. **Social Connectivity & User Profiles** - Users can connect with friends and manage public/private profiles with customizable preferences and notification settings (friend relationships defined in [backend/models.py](backend/models.py)).


