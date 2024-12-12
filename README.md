# Bash API File Handler

## Description

REST API developed with Django and Django REST Framework to run bash scripts and convert output to JSON.

## Technologies Used

- **Django** and **Django REST Framework**
- **PostgreSQL** (via Docker)
- **Docker** and **Docker Compose**

## Setup Instructions

### 1. Clone the repository:

```bash
git clone https://github.com/patriciafelisberto/bash-api-file-handler.git
```

### 2. Configure and Get Started with Docker

```
docker-compose up --build
```

### 3. Apply Migrations and Create Superuser

```
docker-compose exec backend python manage.py makemigrations
```
```
docker-compose exec backend python manage.py migrate
```
```
docker-compose exec backend python manage.py createsuperuser
```

### 4. Access the API

- A API will be available on http://localhost:8000/.

- Swagger: http://localhost:8000/swagger

### 5. Scripts Permission

```
cd src/
chmod +x scripts/*.sh
```

### 6. Tests Execution

```
docker-compose exec backend pytest
```
