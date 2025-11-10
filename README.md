# Car Dealership API

A FastAPI-based inventory management system for a car dealership, with a PostgreSQL backend and an Nginx frontend.

## Prerequisites
- Docker and Docker Compose
- Python 3.11 (for local development without Docker)

## Setup

1. Clone the repository:
   ```bash
   https://github.com/Tom-117/Car-Dealership.git
   cd Car-Dealership/
2. Create a .env file and set your DATABASE_URL
3. Start the service

## Development
The database schema is initialized via ./api/init_db.sql.
Dependencies are listed in requirements.txt

## Notes
This is a non-production project for demonstration purposes.
Ensure the db service is healthy before running the api service.