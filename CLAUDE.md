# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Simple FastAPI login application with CSV-based authentication. The application provides a REST API endpoint for user authentication without a frontend interface.

## Architecture

Single-file application (`main.py`) containing:
- FastAPI application instance
- Pydantic model for login requests (`LoginRequest`)
- CSV-based credential validation function (`validate_credentials`)
- Two endpoints: `/` (welcome message) and `/login` (authentication)

Authentication mechanism reads from a CSV file (`unpw`) in the project root, where each line contains comma-separated username and password.

## Development Commands

**Setup environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

**Run the application:**
```bash
uvicorn main:app --reload
```

**Run in production mode:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Test the login endpoint:**
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_user", "password": "your_pass"}'
```

## Key Dependencies

- FastAPI 0.115.6 - Web framework
- Uvicorn 0.34.0 - ASGI server
- Pydantic 2.10.5 - Data validation

## Credentials File

The `unpw` file contains credentials in CSV format:
- Format: `username,password` (one per line)
- Location: Project root directory
- Read by `validate_credentials()` in main.py:17