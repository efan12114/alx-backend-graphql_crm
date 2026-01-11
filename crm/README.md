# CRM Celery Setup

This document outlines the steps to set up and run the Celery tasks for the CRM application.

## Prerequisites

- Redis must be installed and running on `redis://localhost:6379`.
- All Python dependencies from `requirements.txt` must be installed.

## Setup

1. **Install Redis:**

   Follow the official Redis installation guide for your operating system.

2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run Migrations:**

   ```bash
   python manage.py migrate
   ```

## Running Celery

1. **Start the Celery Worker:**

   ```bash
   celery -A crm worker -l info
   ```

2. **Start Celery Beat:**

   ```bash
   celery -A crm beat -l info
   ```

## Verification

After the scheduled time (Monday at 6:00 AM), check the contents of `/tmp/crm_report_log.txt` to verify that the report was generated successfully.
 # Celery Setup for CRM Reports

## Prerequisites

1. Install Redis:
   ```bash
   sudo apt-get install redis-server
   # or on macOS: brew install redis
   2. Install Celery:
   pip install -r requirements.txt

   1. Apply Database Migrations:
   python manage.py migrate

   2. Start Redis Server
   redis-server
# or start as service: sudo systemctl start redis

   