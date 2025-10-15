# Deployment Guide

This guide provides detailed instructions for deploying the Automated Job Tracker backend, including both the Django REST API and the Celery worker.

## Quick Start

### Local Development (5 Minutes)

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/automated-job-tracker.git
cd automated-job-tracker
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Set environment variables
# Create .env file with configuration (see Environment Variables section)

# 3. Setup database
python manage.py migrate
python manage.py collectstatic --noinput

# 4. Run (3 separate terminals)
# Terminal 1: API
python manage.py runserver

# Terminal 2: Celery Worker
celery -A jobtracker_backend_api worker --loglevel=info --pool=solo  # Windows
# celery -A jobtracker_backend_api worker --loglevel=info  # macOS/Linux

# Terminal 3: RabbitMQ
rabbitmq-server
```

### Docker (2 Minutes)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/automated-job-tracker.git
cd automated-job-tracker

# 2. Create .env file with your configuration

# 3. Run everything
docker-compose up -d

# 4. Run migrations
docker-compose run web python manage.py migrate
```

### Production Deployment

- **Heroku**: See [Option 1: Heroku](#option-1-heroku) - Easiest, click-and-deploy
- **Render**: See [Option 2: Render](#option-2-render) - Modern, generous free tier
- **Docker**: See [Option 3: Docker](#option-3-docker) - Portable, consistent
- **VPS**: See [Option 4: VPS](#option-4-vps-digitaloceanawsgcp) - Full control

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Local Development Setup](#local-development-setup)
- [Production Deployment](#production-deployment)
  - [Option 1: Heroku](#option-1-heroku)
  - [Option 2: Render](#option-2-render)
  - [Option 3: Docker](#option-3-docker)
  - [Option 4: VPS (DigitalOcean/AWS/GCP)](#option-4-vps-digitaloceanawsgcp)
- [Database Setup](#database-setup)
- [Redis Setup](#redis-setup)
- [Running the Application](#running-the-application)
- [Monitoring and Logs](#monitoring-and-logs)
- [Troubleshooting](#troubleshooting)

---

## Architecture Overview

The application consists of three main components that must be deployed:

1. **Django REST API** (Web Server)
   - Handles HTTP requests
   - Serves the REST API endpoints
   - Manages authentication and authorization

2. **Celery Worker** (Background Task Processor)
   - Processes asynchronous email fetching tasks
   - Communicates with Gmail API and OpenAI API
   - Updates Google Sheets

3. **Supporting Services**
   - **PostgreSQL**: Database for storing users, jobs, and fetch logs
   - **RabbitMQ**: Message broker for Celery task queue

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP
       ↓
┌─────────────────────┐
│   Django API        │←──┐
│   (Gunicorn)        │   │
└──────┬──────────────┘   │
       │                  │
       ↓                  │
┌─────────────────────┐   │
│   PostgreSQL        │   │
└─────────────────────┘   │
                          │
       ┌──────────────────┘
       │
       ↓
┌─────────────────────┐
│   RabbitMQ Broker   │
└──────┬──────────────┘
       │
       ↓
┌─────────────────────┐
│   Celery Worker     │
└──────┬──────────────┘
       │
       ├──→ Gmail API
       ├──→ OpenAI API
       └──→ Google Sheets API
```

---

## Prerequisites

### Required Accounts and API Keys

1. **Google Cloud Console** (for OAuth and APIs)
   - Gmail API enabled
   - Google Sheets API enabled
   - OAuth 2.0 credentials created

2. **OpenAI Account**
   - API key for GPT-4o-mini

3. **Hosting Platform Account** (choose one)
   - Heroku
   - Render
   - DigitalOcean/AWS/GCP
   - Or local machine for development

### Required Software (for local development)

- Python 3.10+
- PostgreSQL 14+
- RabbitMQ 3.12+
- Git

---

## Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Django Settings
SECRET_KEY=your-super-secret-django-key-change-this-in-production
DEBUG=false
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost
CORS_ALLOWED_ORIGINS=https://yourdomain.com,http://localhost:3000
CSRF_TRUSTED_ORIGINS=https://yourdomain.com

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=jobtracker_db
DB_USER=jobtracker_user
DB_PASSWORD=your-secure-database-password
DB_HOST=localhost
DB_PORT=5432

# RabbitMQ Configuration
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=rpc://

# Google OAuth Configuration
GOOGLE_API_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_API_CLIENT_SECRET=your-client-secret
GOOGLE_API_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_API_USER_INFO_URI=https://www.googleapis.com/oauth2/v1/userinfo
GOOGLE_API_REDIRECT_URI=https://yourdomain.com/auth/google/callback/
GOOGLE_API_SCOPE=openid email profile https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/spreadsheets

# Frontend Configuration
FRONTEND_REDIRECT_URL=https://yourdomain.com/dashboard

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key

# Celery Configuration
FETCH_BATCH_SIZE=10

# Mock Mode (for testing without real APIs)
MOCK_MODE=false
```

### Development Environment Variables

For local development, use these settings:

```bash
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
DB_HOST=localhost
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=rpc://
FRONTEND_REDIRECT_URL=http://localhost:3000/dashboard
```

---

## Local Development Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/automated-job-tracker.git
cd automated-job-tracker
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: The `requirements.txt` includes `amqp` which is required for Celery to work with RabbitMQ. If you need to install it separately:
```bash
pip install celery[amqp]
```

### Step 4: Set Up Environment Variables

Create a `.env` file with the development configuration shown above.

### Step 5: Set Up PostgreSQL

```bash
# Install PostgreSQL (if not already installed)
# Windows: Download from https://www.postgresql.org/download/windows/
# macOS: brew install postgresql
# Linux: sudo apt-get install postgresql

# Create database and user
psql -U postgres

# In PostgreSQL shell:
CREATE DATABASE jobtracker_db;
CREATE USER jobtracker_user WITH PASSWORD 'your-password';
ALTER ROLE jobtracker_user SET client_encoding TO 'utf8';
ALTER ROLE jobtracker_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE jobtracker_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE jobtracker_db TO jobtracker_user;
\q
```

### Step 6: Set Up RabbitMQ

```bash
# Windows: Download from https://www.rabbitmq.com/install-windows.html
# Or use WSL with: sudo apt-get install rabbitmq-server

# macOS
brew install rabbitmq
brew services start rabbitmq

# Linux
sudo apt-get install rabbitmq-server
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server

# Enable management plugin (optional, provides web UI on port 15672)
sudo rabbitmq-plugins enable rabbitmq_management
```

### Step 7: Run Migrations

```bash
python manage.py migrate
```

### Step 8: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### Step 9: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 10: Run the Application

**Terminal 1 - Django API:**
```bash
python manage.py runserver 0.0.0.0:8000
```

**Terminal 2 - Celery Worker:**
```bash
# Windows
celery -A jobtracker_backend_api worker --loglevel=info --pool=solo

# macOS/Linux
celery -A jobtracker_backend_api worker --loglevel=info
```

**Terminal 3 - RabbitMQ (if not running as service):**
```bash
rabbitmq-server
```

### Step 11: Test the Setup

Visit `http://localhost:8000/` to see the API root.

---

## Production Deployment

### Option 1: Heroku

Heroku makes it easy to deploy Django applications with built-in support for PostgreSQL and Redis.

#### Prerequisites

- Heroku CLI installed
- Heroku account

#### Step 1: Create Heroku App

```bash
heroku login
heroku create your-app-name
```

#### Step 2: Add Buildpacks

```bash
heroku buildpacks:set heroku/python
```

#### Step 3: Add Add-ons

```bash
# PostgreSQL
heroku addons:create heroku-postgresql:mini

# CloudAMQP (RabbitMQ)
heroku addons:create cloudamqp:lemur
```

#### Step 4: Set Environment Variables

```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=false
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
heroku config:set CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
heroku config:set GOOGLE_API_CLIENT_ID=your-client-id
heroku config:set GOOGLE_API_CLIENT_SECRET=your-client-secret
heroku config:set GOOGLE_API_REDIRECT_URI=https://your-app-name.herokuapp.com/auth/google/callback/
heroku config:set GOOGLE_API_SCOPE="openid email profile https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/spreadsheets"
heroku config:set OPENAI_API_KEY=your-openai-key
heroku config:set FRONTEND_REDIRECT_URL=https://your-frontend-domain.com/dashboard
```

Heroku automatically sets `DATABASE_URL` and `CLOUDAMQP_URL`. Update `settings.py` to use these:

```python
import dj_database_url

# Add to settings.py
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

if 'CLOUDAMQP_URL' in os.environ:
    CELERY_BROKER_URL = os.environ['CLOUDAMQP_URL']
    CELERY_RESULT_BACKEND = 'rpc://'
```

#### Step 5: Update Procfile

Update the `Procfile` to include both web and worker processes:

```
web: gunicorn jobtracker_backend_api.wsgi --log-file -
worker: celery -A jobtracker_backend_api worker --loglevel=info
```

#### Step 6: Deploy

```bash
git add .
git commit -m "Configure for Heroku deployment"
git push heroku main
```

#### Step 7: Run Migrations

```bash
heroku run python manage.py migrate
```

#### Step 8: Scale Workers

```bash
# Scale web dynos
heroku ps:scale web=1

# Scale celery worker
heroku ps:scale worker=1
```

#### Step 9: View Logs

```bash
# All logs
heroku logs --tail

# Worker logs only
heroku logs --tail --dyno worker
```

---

### Option 2: Render

Render provides similar functionality to Heroku with a modern interface.

#### Step 1: Create Account

Sign up at [render.com](https://render.com)

#### Step 2: Create PostgreSQL Database

1. Go to Dashboard → New → PostgreSQL
2. Name: `jobtracker-db`
3. Select plan (free or paid)
4. Note the Internal Database URL

#### Step 3: Create RabbitMQ Instance

**Note**: Render doesn't have native RabbitMQ support. Use CloudAMQP:
1. Sign up at [cloudamqp.com](https://www.cloudamqp.com/)
2. Create a new instance (free tier available)
3. Note the AMQP URL (e.g., `amqp://user:pass@host:5672/vhost`)

#### Step 4: Create Web Service

1. Go to Dashboard → New → Web Service
2. Connect your GitHub repository
3. Configure:
   - **Name**: `jobtracker-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `gunicorn jobtracker_backend_api.wsgi:application`
   - **Plan**: Select appropriate plan

4. Add Environment Variables (in Environment tab):
   - All variables from the Environment Variables section above
   - Use the PostgreSQL Internal URL for database connection
   - Use the CloudAMQP URL for Celery broker

#### Step 5: Create Background Worker

1. Go to Dashboard → New → Background Worker
2. Connect same repository
3. Configure:
   - **Name**: `jobtracker-worker`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `celery -A jobtracker_backend_api worker --loglevel=info`
   - **Plan**: Select appropriate plan

4. Add same Environment Variables as the web service

#### Step 6: Deploy

Render automatically deploys when you push to your connected branch.

---

### Option 3: Docker

Docker deployment provides consistency across environments.

#### Step 1: Create Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations (will be done in docker-compose)
# RUN python manage.py migrate

EXPOSE 8000

CMD ["gunicorn", "jobtracker_backend_api.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### Step 2: Create docker-compose.yml

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:14-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=jobtracker_db
      - POSTGRES_USER=jobtracker_user
      - POSTGRES_PASSWORD=secure_password_here
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U jobtracker_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build: .
    command: gunicorn jobtracker_backend_api.wsgi:application --bind 0.0.0.0:8000 --workers 3
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - DB_HOST=db
      - DB_PORT=5432
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  worker:
    build: .
    command: celery -A jobtracker_backend_api worker --loglevel=info
    volumes:
      - .:/app
    env_file:
      - .env
    environment:
      - DB_HOST=db
      - DB_PORT=5432
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

volumes:
  postgres_data:
  static_volume:
```

#### Step 3: Create .dockerignore

Create `.dockerignore`:

```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
*.sqlite3
.env
.git
.gitignore
*.md
notebooks/
```

#### Step 4: Build and Run

```bash
# Build images
docker-compose build

# Run migrations
docker-compose run web python manage.py migrate

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View worker logs only
docker-compose logs -f worker
```

#### Step 5: Stop Services

```bash
docker-compose down

# Remove volumes (database data)
docker-compose down -v
```

---

### Option 4: VPS (DigitalOcean/AWS/GCP)

Deploying on a VPS gives you full control but requires more configuration.

#### Prerequisites

- VPS with Ubuntu 22.04 LTS
- Root or sudo access
- Domain name (optional but recommended)

#### Step 1: Initial Server Setup

```bash
# SSH into your server
ssh root@your_server_ip

# Update system
apt update && apt upgrade -y

# Create application user
adduser jobtracker
usermod -aG sudo jobtracker
su - jobtracker
```

#### Step 2: Install Dependencies

```bash
# Install Python and dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib rabbitmq-server nginx supervisor git

# Install certbot (for SSL)
sudo apt install -y certbot python3-certbot-nginx
```

#### Step 3: Set Up PostgreSQL

```bash
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE jobtracker_db;
CREATE USER jobtracker_user WITH PASSWORD 'secure_password';
ALTER ROLE jobtracker_user SET client_encoding TO 'utf8';
ALTER ROLE jobtracker_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE jobtracker_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE jobtracker_db TO jobtracker_user;
\q
```

#### Step 4: Set Up RabbitMQ

```bash
# RabbitMQ is already installed, configure it to start on boot
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server

# Enable management plugin (optional, provides web UI on port 15672)
sudo rabbitmq-plugins enable rabbitmq_management

# Create a new user for production (recommended)
sudo rabbitmqctl add_user jobtracker your_secure_password
sudo rabbitmqctl set_user_tags jobtracker administrator
sudo rabbitmqctl set_permissions -p / jobtracker ".*" ".*" ".*"
```

#### Step 5: Clone and Set Up Application

```bash
cd /home/jobtracker
git clone https://github.com/yourusername/automated-job-tracker.git
cd automated-job-tracker

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
# Paste your environment variables
```

#### Step 6: Run Migrations

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

#### Step 7: Set Up Gunicorn

Create Gunicorn systemd service:

```bash
sudo nano /etc/systemd/system/jobtracker.service
```

Paste the following:

```ini
[Unit]
Description=Jobtracker Gunicorn Daemon
After=network.target

[Service]
User=jobtracker
Group=www-data
WorkingDirectory=/home/jobtracker/automated-job-tracker
Environment="PATH=/home/jobtracker/automated-job-tracker/venv/bin"
EnvironmentFile=/home/jobtracker/automated-job-tracker/.env
ExecStart=/home/jobtracker/automated-job-tracker/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/home/jobtracker/automated-job-tracker/jobtracker.sock \
    jobtracker_backend_api.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### Step 8: Set Up Celery Worker

Create Celery systemd service:

```bash
sudo nano /etc/systemd/system/jobtracker-worker.service
```

Paste the following:

```ini
[Unit]
Description=Jobtracker Celery Worker
After=network.target rabbitmq-server.service

[Service]
Type=forking
User=jobtracker
Group=jobtracker
WorkingDirectory=/home/jobtracker/automated-job-tracker
Environment="PATH=/home/jobtracker/automated-job-tracker/venv/bin"
EnvironmentFile=/home/jobtracker/automated-job-tracker/.env
ExecStart=/home/jobtracker/automated-job-tracker/venv/bin/celery -A jobtracker_backend_api worker \
    --loglevel=info \
    --logfile=/var/log/celery/worker.log \
    --pidfile=/var/run/celery/worker.pid \
    --detach

[Install]
WantedBy=multi-user.target
```

Create log directory:

```bash
sudo mkdir -p /var/log/celery /var/run/celery
sudo chown jobtracker:jobtracker /var/log/celery /var/run/celery
```

#### Step 9: Set Up Nginx

```bash
sudo nano /etc/nginx/sites-available/jobtracker
```

Paste the following:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        root /home/jobtracker/automated-job-tracker;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/jobtracker/automated-job-tracker/jobtracker.sock;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/jobtracker /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 10: Enable SSL with Let's Encrypt

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

#### Step 11: Start All Services

```bash
# Start and enable Gunicorn
sudo systemctl start jobtracker
sudo systemctl enable jobtracker

# Start and enable Celery worker
sudo systemctl start jobtracker-worker
sudo systemctl enable jobtracker-worker

# Check status
sudo systemctl status jobtracker
sudo systemctl status jobtracker-worker
```

#### Step 12: Set Up Automatic Restarts

Configure supervisor for auto-restart on failure:

```bash
sudo apt install supervisor
sudo nano /etc/supervisor/conf.d/jobtracker.conf
```

Paste:

```ini
[program:jobtracker]
command=/home/jobtracker/automated-job-tracker/venv/bin/gunicorn --workers 3 --bind unix:/home/jobtracker/automated-job-tracker/jobtracker.sock jobtracker_backend_api.wsgi:application
directory=/home/jobtracker/automated-job-tracker
user=jobtracker
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/jobtracker/gunicorn.log

[program:jobtracker-worker]
command=/home/jobtracker/automated-job-tracker/venv/bin/celery -A jobtracker_backend_api worker --loglevel=info
directory=/home/jobtracker/automated-job-tracker
user=jobtracker
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/jobtracker/celery.log
```

Create log directory and reload:

```bash
sudo mkdir -p /var/log/jobtracker
sudo chown jobtracker:jobtracker /var/log/jobtracker
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status
```

---

## Database Setup

### PostgreSQL Configuration

#### Production Settings

For production, ensure these PostgreSQL settings are optimized:

```sql
-- Connect to your database
\c jobtracker_db

-- Set connection pooling
ALTER DATABASE jobtracker_db SET max_connections = 100;

-- Enable performance optimizations
ALTER DATABASE jobtracker_db SET shared_buffers = '256MB';
ALTER DATABASE jobtracker_db SET effective_cache_size = '1GB';
```

#### Backup and Restore

**Backup:**
```bash
# Local backup
pg_dump -U jobtracker_user jobtracker_db > backup.sql

# With timestamp
pg_dump -U jobtracker_user jobtracker_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

**Restore:**
```bash
psql -U jobtracker_user jobtracker_db < backup.sql
```

#### Automated Backups

Create a backup script:

```bash
nano ~/backup_db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/jobtracker/backups"
DB_NAME="jobtracker_db"
DB_USER="jobtracker_user"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

Make executable and add to cron:

```bash
chmod +x ~/backup_db.sh
crontab -e

# Add this line (runs daily at 2 AM)
0 2 * * * /home/jobtracker/backup_db.sh
```

---

## RabbitMQ Setup

### RabbitMQ Configuration

For production, configure RabbitMQ properly:

```bash
# Create RabbitMQ configuration file
sudo nano /etc/rabbitmq/rabbitmq.conf
```

Key settings:

```conf
# Bind to localhost for security (if on same server)
listeners.tcp.local = 127.0.0.1:5672

# Enable management plugin
management.tcp.port = 15672

# Set resource limits
vm_memory_high_watermark.relative = 0.6
disk_free_limit.relative = 2.0
```

Create a production user:

```bash
# Add user
sudo rabbitmqctl add_user jobtracker_user your_secure_password

# Set permissions
sudo rabbitmqctl set_permissions -p / jobtracker_user ".*" ".*" ".*"

# Delete default guest user (security)
sudo rabbitmqctl delete_user guest
```

Restart RabbitMQ:

```bash
sudo systemctl restart rabbitmq-server
```

Update your `.env`:

```bash
CELERY_BROKER_URL=amqp://jobtracker_user:your_secure_password@localhost:5672//
CELERY_RESULT_BACKEND=rpc://
```

### RabbitMQ Management UI

Access the management interface at `http://your-server:15672` (or `http://localhost:15672` locally).

**Default credentials** (for development only):
- Username: `guest`
- Password: `guest`

**Production**: Use the `jobtracker_user` credentials you created above.

---

## Running the Application

### Production Commands

#### Start Services

```bash
# Using systemd (VPS)
sudo systemctl start jobtracker
sudo systemctl start jobtracker-worker

# Using Docker
docker-compose up -d

# Using Heroku
heroku ps:scale web=1 worker=1

# Manual (not recommended for production)
gunicorn jobtracker_backend_api.wsgi:application --bind 0.0.0.0:8000 &
celery -A jobtracker_backend_api worker --loglevel=info &
```

#### Stop Services

```bash
# Using systemd
sudo systemctl stop jobtracker
sudo systemctl stop jobtracker-worker

# Using Docker
docker-compose down

# Using Heroku
heroku ps:scale web=0 worker=0
```

#### Restart Services

```bash
# Using systemd
sudo systemctl restart jobtracker
sudo systemctl restart jobtracker-worker

# Using Docker
docker-compose restart

# Using Heroku
heroku restart
```

---

## Monitoring and Logs

### View Logs

#### Django API Logs

```bash
# Systemd
sudo journalctl -u jobtracker -f

# Supervisor
tail -f /var/log/jobtracker/gunicorn.log

# Docker
docker-compose logs -f web

# Heroku
heroku logs --tail --dyno web
```

#### Celery Worker Logs

```bash
# Systemd
sudo journalctl -u jobtracker-worker -f

# Supervisor
tail -f /var/log/jobtracker/celery.log

# Docker
docker-compose logs -f worker

# Heroku
heroku logs --tail --dyno worker
```

### Monitoring Tools

#### Celery Flower (Web-based monitoring)

Install Flower:

```bash
pip install flower
```

Add to Procfile or systemd:

```bash
# Run Flower
celery -A jobtracker_backend_api flower --port=5555
```

Access at `http://your-domain:5555`

#### Health Check Endpoint

Add to `urls.py`:

```python
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        "status": "healthy",
        "database": "connected" if check_db() else "disconnected",
        "redis": "connected" if check_redis() else "disconnected"
    })

# Add to urlpatterns
path('health/', health_check),
```

---

## Troubleshooting

### Common Issues

#### 1. Celery Worker Not Processing Tasks

**Symptoms**: Tasks stay in PENDING state

**Solutions**:
```bash
# Check if worker is running
ps aux | grep celery

# Check RabbitMQ connection
sudo rabbitmqctl status

# Check RabbitMQ queues
sudo rabbitmqctl list_queues

# Restart worker
sudo systemctl restart jobtracker-worker

# Check worker logs
sudo journalctl -u jobtracker-worker -f
```

#### 2. Database Connection Errors

**Symptoms**: `OperationalError: could not connect to server`

**Solutions**:
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database exists
sudo -u postgres psql -l

# Test connection
psql -U jobtracker_user -d jobtracker_db -h localhost

# Check environment variables
echo $DB_HOST $DB_PORT $DB_NAME
```

#### 3. Static Files Not Loading

**Symptoms**: 404 errors for CSS/JS files

**Solutions**:
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check STATIC_ROOT in settings.py
python manage.py diffsettings | grep STATIC

# Check Nginx configuration
sudo nginx -t
sudo systemctl reload nginx
```

#### 4. CORS Errors

**Symptoms**: Browser console shows CORS policy errors

**Solutions**:
```bash
# Check CORS settings in .env
echo $CORS_ALLOWED_ORIGINS

# Ensure frontend URL is in CORS_ALLOWED_ORIGINS
# Example: CORS_ALLOWED_ORIGINS=https://frontend.com,http://localhost:3000

# Restart application
sudo systemctl restart jobtracker
```

#### 5. Gmail API Authentication Errors

**Symptoms**: "User not authorized" or token expired

**Solutions**:
- Verify Google OAuth credentials
- Check redirect URI matches exactly
- Ensure Gmail API is enabled in Google Cloud Console
- Verify scopes include Gmail and Sheets access
- Check if tokens are being saved to database

#### 6. OpenAI API Errors

**Symptoms**: "Invalid API key" or rate limit errors

**Solutions**:
```bash
# Verify API key
echo $OPENAI_API_KEY

# Check OpenAI account balance and rate limits
# Implement exponential backoff for rate limiting
```

### Performance Optimization

#### 1. Increase Gunicorn Workers

```bash
# Calculate: (2 x CPU cores) + 1
gunicorn jobtracker_backend_api.wsgi:application --workers 5 --bind 0.0.0.0:8000
```

#### 2. Add Celery Concurrency

```bash
# Increase concurrent workers
celery -A jobtracker_backend_api worker --concurrency=4 --loglevel=info
```

#### 3. Enable Database Connection Pooling

Install pgbouncer:

```bash
sudo apt install pgbouncer
```

#### 4. Add Caching

If you want to add caching with Redis (separate from RabbitMQ):

```bash
# Install Redis (separate from RabbitMQ)
sudo apt install redis-server

# Install django-redis
pip install django-redis
```

```python
# Add to settings.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",  # Use different DB from broker
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
```

### Security Checklist

- [ ] Change `SECRET_KEY` to a unique, random value
- [ ] Set `DEBUG=false` in production
- [ ] Use HTTPS (SSL/TLS certificate)
- [ ] Set secure database passwords
- [ ] Create RabbitMQ user with strong password (don't use guest in production)
- [ ] Configure RabbitMQ to bind to localhost only (if on same server)
- [ ] Set up firewall rules
- [ ] Keep dependencies updated
- [ ] Set up regular database backups
- [ ] Monitor logs for suspicious activity
- [ ] Use environment variables for all secrets
- [ ] Enable CSRF protection
- [ ] Configure proper CORS settings
- [ ] Set secure cookie settings

---

## Maintenance

### Regular Tasks

#### Daily
- Monitor error logs
- Check Celery worker status
- Verify email fetching is working

#### Weekly
- Review application performance
- Check database size and performance
- Update dependencies (test first)

#### Monthly
- Rotate logs
- Review and clean old data
- Test backup restoration
- Update SSL certificates (if not automatic)

### Updating the Application

```bash
# Pull latest code
cd /home/jobtracker/automated-job-tracker
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart jobtracker
sudo systemctl restart jobtracker-worker
```

---

## Support

For issues or questions:

1. Check the [README.md](README.md) for general information
2. Review [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
3. Open an issue on GitHub
4. Check existing issues and discussions

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

