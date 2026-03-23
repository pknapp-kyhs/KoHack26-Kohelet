# 2Jew List - Dependencies & Libraries Guide

This document explains all the libraries and packages imported in the 2Jew List application.

---

## Standard Library (Built-in Python Packages)

### `datetime`
**Import:** `from datetime import date, datetime, timedelta`
**Purpose:** Handles date and time operations
**Used for:**
- Creating and manipulating dates/times in the app
- Tracking user streaks with start/end dates
- Storing timestamps for user checklist items
- Calculating time intervals (e.g., streak duration)

### `typing`
**Import:** `from typing import Any, Dict, List, Optional`
**Purpose:** Provides type hints for better code clarity and IDE support
**Used for:**
- Annotating function parameters and return types
- Specifying data structure types (e.g., `List[str]`, `Dict[str, Any]`)
- Improving code documentation and error detection

### `json`
**Import:** `import json`
**Purpose:** Serializes and deserializes JSON data
**Used for:**
- Parsing JSON request/response bodies in the API
- Storing user preferences as JSON strings in the database
- Converting Python objects to JSON for API responses

### `os`
**Import:** `import os`
**Purpose:** Interfaces with the operating system
**Used for:**
- Getting environment variables
- File path operations (building paths to frontend directory)
- Checking if files exist

### `calendar`
**Import:** `import calendar`
**Purpose:** Provides calendar-related functions
**Used for:**
- Generating calendar grids for month views
- Calculating days of the week
- Building calendar event displays

### `uuid`
**Import:** `import uuid`
**Purpose:** Generates universally unique identifiers
**Used for:**
- Creating unique IDs for database records (instead of auto-increment)
- Ensuring globally unique identifiers across systems

### `pathlib`
**Import:** `from pathlib import Path`
**Purpose:** Object-oriented file path handling
**Used for:**
- File path operations in scripts
- Cross-platform path management

---

## Third-Party Libraries (from requirements.txt)

### `FastAPI` 
**Import:** `from fastapi import FastAPI, HTTPException, Depends, Header, status, Query`
**Import:** `from fastapi.staticfiles import StaticFiles`
**Import:** `from fastapi.responses import FileResponse`
**Version:** 0.115.3
**Purpose:** Modern, fast web framework for building APIs
**Key Features:**
- Automatic API documentation (Swagger UI)
- Dependency injection system
- Request/response validation
- CORS support
- WebSocket support
**Used for:**
- Creating all REST API endpoints (login, profile, rewards, etc.)
- Serving static frontend files
- Handling HTTP requests/responses
- Auto-generating API documentation

### `SQLAlchemy`
**Import:** `from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Date, Text, create_engine`
**Import:** `from sqlalchemy.orm import Session, relationship, sessionmaker, DeclarativeBase`
**Version:** 2.0.22
**Purpose:** Object-Relational Mapping (ORM) library for database operations
**Key Features:**
- Maps Python classes to database tables
- Query builder with intuitive syntax
- Relationship management (foreign keys)
- Migration support
**Used for:**
- Defining database models (User, Task, ChecklistItem, etc.)
- Creating table schemas
- Querying data from SQLite database
- Managing database relationships

### `Pydantic`
**Import:** `from pydantic import BaseModel, EmailStr, field_validator`
**Version:** 2.8.0
**Purpose:** Data validation and serialization using Python type hints
**Key Features:**
- Runtime type checking
- Automatic JSON serialization
- Custom validators
- Email validation
**Used for:**
- Defining request/response schemas for API endpoints
- Validating incoming request data
- Converting database models to JSON responses
- Ensuring data type safety

### `python-jose`
**Import:** `from jose import JWTError, jwt`
**Version:** 3.1.0
**Purpose:** JWT (JSON Web Token) library for secure authentication
**Key Features:**
- Creates and validates JWTs
- Claims encapsulation
- Cryptographic signing
**Used for:**
- Creating access tokens on login/registration
- Validating tokens in protected endpoints
- Extracting user ID from tokens
- Session management without server-side storage

### `passlib`
**Import:** `from passlib.context import CryptContext`
**Version:** 1.7.4
**Purpose:** Password hashing and verification library
**Key Features:**
- Secure password hashing (bcrypt, PBKDF2, etc.)
- Configurable hash algorithms
- Defense against rainbow table attacks
**Used for:**
- Hashing user passwords during registration
- Verifying passwords during login
- Never storing plain-text passwords

### `holidays`
**Import:** `import holidays`
**Version:** 0.35
**Purpose:** Library for working with holidays and observances
**Features:**
- Supports Jewish holidays (Passover, Rosh Hashanah, etc.)
- Supports US and other national holidays
- Easy date-to-holiday lookup
**Used for:**
- Displaying Jewish holidays on calendar
- Showing US holidays on calendar
- Holiday context for daily tasks
- Calendar event enrichment

### `requests`
**Import:** `import requests`
**Version:** 2.32.5
**Purpose:** HTTP client library for making web requests
**Key Features:**
- Simple HTTP requests (GET, POST, PUT, DELETE)
- Session management
- JSON handling
- Error handling
**Used for:**
- Making API calls (if integrating with external services)
- Testing endpoints
- Fetching external data

### `geopy`
**Import:** `from geopy.geocoders import Nominatim`
**Import:** `from geopy.exc import GeocoderTimedOut, GeocoderServiceError`
**Version:** 2.4.1
**Purpose:** Geocoding library (converting addresses ↔ coordinates)
**Key Features:**
- Multiple geocoder providers (Google, OpenStreetMap, etc.)
- Reverse geocoding (coordinates → address)
- Error handling for timeouts/service issues
**Used for:**
- Converting zip codes to coordinates for Zmanim calculation
- Finding location-based information
- Calculating prayer times based on geographic location

### `Uvicorn`
**Import:** Used as server runner (not directly imported)
**Version:** 0.24.0
**Purpose:** ASGI web server for running FastAPI applications
**Features:**
- High performance
- Auto-reload in development mode
- WebSocket support
**Used for:**
- Running the FastAPI backend server
- Hot-reload during development (`--reload` flag)
- Production server deployment

---

## Summary Table

| Library | Type | Purpose | Critical? |
|---------|------|---------|-----------|
| FastAPI | Framework | Web API framework | ✅ YES |
| SQLAlchemy | Database | ORM for database operations | ✅ YES |
| Pydantic | Validation | Request/response validation | ✅ YES |
| python-jose | Security | JWT authentication | ✅ YES |
| passlib | Security | Password hashing | ✅ YES |
| datetime | Built-in | Date/time operations | ✅ YES |
| typing | Built-in | Type hints | ⚠️ Supporting |
| holidays | Feature | Holiday calendar | ⚠️ Feature |
| geopy | Feature | Geocoding for location | ⚠️ Feature |
| requests | HTTP | HTTP client requests | ⚠️ Feature |
| json, os, calendar, uuid | Built-in | Utility functions | ⚠️ Supporting |

---

## Dependency Version Info

All dependencies are defined in `requirements.txt`:
```
fastapi==0.115.3
uvicorn==0.24.0
SQLAlchemy==2.0.22
pydantic==2.8.0
pydantic[email]
passlib==1.7.4
python-jose[cryptography]==3.1.0
python-dateutil==2.8.2
holidays==0.35
requests==2.31.0
geopy==2.4.1
```

To install all dependencies:
```bash
pip install -r requirements.txt
```

---

## Key Architecture Notes

### Security Stack
- **Authentication:** python-jose (JWT tokens)
- **Password Security:** passlib (bcrypt hashing)
- **Data Validation:** Pydantic (type-safe requests/responses)

### Data Persistence
- **ORM:** SQLAlchemy (Python ↔ SQL abstraction)
- **Database:** SQLite (file-based, lightweight)
- **Serialization:** Pydantic (Python ↔ JSON)

### API Layer
- **Framework:** FastAPI (async, type-hinted)
- **Server:** Uvicorn (ASGI)
- **Request/Response:** JSON via Pydantic

### Feature Modules
- **Calendar:** holidays library + calendar module
- **Geolocation:** geopy + Nominatim geocoder
- **HTTP:** requests library for external APIs

---

**Last Updated:** March 23, 2026
**Project:** 2Jew List - Jewish Daily Habit Tracker
