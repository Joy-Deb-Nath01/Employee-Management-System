# Employee Management System (EMS Pro)

EMS Pro is a modern, responsive web application for managing company workforce schedules, attendance check-ins/check-outs, leave tracking with balance rules, and organizational department mappings.

## Tech Stack
- **Backend**: Python 3.12+, Django 5.0+
- **Database**: PostgreSQL (with SQLite3 fallback for local development)
- **Frontend**: Django Templates + Bootstrap 5 (with Bootstrap Icons)
- **Authentication**: Custom Django User Roles (`ADMIN`, `HR`, `EMPLOYEE`)

---

## Installation & Setup

Follow these steps to run the application locally:

### 1. Clone & Prepare Directory
Make sure you are in the project folder containing `manage.py`.

### 2. Set Up Virtual Environment
Create and activate a virtual environment to manage dependencies:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install all required Python packages:
```bash
pip install -r requirements.txt
```

### 4. Create and Configure `.env` File
Create a `.env` file in the root of the project (same directory as `manage.py`) by copying `.env.example`:
```bash
cp .env.example .env
```
Open `.env` and fill in the values:
```ini
# Django Settings
SECRET_KEY=django-insecure-replace-this-with-a-real-secret-key-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration (PostgreSQL credentials)
DB_NAME=ems_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=127.0.0.1
DB_PORT=5432

# Email Configuration (for console email backend in dev)
EMAIL_HOST=localhost
EMAIL_PORT=1025
```

> [!NOTE]
> **PostgreSQL Fallback**: If settings.py cannot connect to the PostgreSQL credentials provided in `.env`, it will print a warning and automatically fall back to a local SQLite database (`db.sqlite3`), allowing the app to run out-of-the-box.

---

## Creating the PostgreSQL Database

If you wish to run the app with PostgreSQL, make sure your PostgreSQL server is running and create the database named in your `.env` file:
```sql
CREATE DATABASE ems_db;
```

---

## Running Database Migrations

Apply database schemas to the configured database:
```bash
python manage.py makemigrations accounts departments employees attendance leave
python manage.py migrate
```

---

## Seeding Sample Test Data

EMS Pro provides a built-in seeding command to populate departments, mock employees, attendance logs, and leave requests for testing:
```bash
python manage.py seed_ems
```

### Seeded Credentials for Testing:
| Role | Username | Password | Notes |
|---|---|---|---|
| **Admin** | `admin` | `AdminPassword123` | System Administrator dashboard access |
| **HR / Manager** | `manager` | `ManagerPassword123` | Department approvals, review leaves, and add employees |
| **Employee 1** | `dev1` | `EmployeePassword123` | Clock-in states, leave requests (Alice Smith) |
| **Employee 2** | `dev2` | `EmployeePassword123` | Backend developer dashboard (Bob Johnson) |
| **Employee 3** | `market1` | `EmployeePassword123` | Marketing lead dashboard (Charlie Brown) |

---

## Running the Development Server

Start the Django development server:
```bash
python manage.py runserver
```
Navigate to [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.
