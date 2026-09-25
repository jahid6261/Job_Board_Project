# 💼 Job Board API

A production-style **Job Board REST API** built with **FastAPI**, designed to connect job seekers with employers through a secure and scalable backend system.

The platform supports **Admin, Employer, and Job Seeker** roles with JWT authentication, employer approval, company management, job posting, job search, resume management, job applications, application status management, email notifications, PostgreSQL, Cloudinary, Alembic, and Docker

## 🚀 Features

* 🔐 JWT Authentication & Role-Based Access Control
* 👥 Admin, Employer & Job Seeker roles
* 📧 Email Account Activation & Notifications
* 🏢 Employer Request & Approval System
* 🏢 Company Management
* 💼 Job Posting & Management
* 🔎 Job Search, Filtering & Pagination
* 📄 Resume Upload & Management
* 📝 Job Application System
* 📊 Admin & Employer Dashboard
* ☁️ Cloudinary File Storage
* 🗄️ PostgreSQL Database
* 🔄 Alembic Database Migration
* 🐳 Docker Support
* 📚 Swagger / OpenAPI Documentation

## 👥 User Roles

### 👑 Admin

* Manage users
* Approve/reject employer requests
* Manage jobs, companies & applications
* View dashboard

### 🏢 Employer

* Create/manage company
* Create/manage jobs
* View applicants
* Update application status
* View dashboard

### 👨‍💼 Job Seeker

* Browse & search jobs
* Manage profile & resume
* Apply for jobs
* Track application status

## 🔄 Application Flow

```text
Job Seeker
    ↓
Browse Jobs
    ↓
Apply with Resume
    ↓
Employer Reviews
    ↓
Accepted / Rejected
    ↓
Email Notification
```

## 🛠️ Tech Stack

| Technology | Purpose          |
| ---------- | ---------------- |
| Python     | Programming      |
| FastAPI    | Backend          |
| PostgreSQL | Database         |
| SQLAlchemy | ORM              |
| Alembic    | Migration        |
| Pydantic   | Validation       |
| JWT        | Authentication   |
| Cloudinary | File Storage     |
| Docker     | Containerization |
| Uvicorn    | ASGI Server      |

## 📁 Project Structure

```text
Job_Board_Project/
├── src/
│   ├── Admin/
│   ├── users/
│   ├── companies/
│   ├── jobs/
│   ├── applications/
│   ├── resumes/
│   ├── categories/
│   ├── depends/
│   └── utils/
├── alembic/
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## ⚙️ Installation

```bash
git clone https://github.com/jahid6261/Job_Board_Project.git
cd Job_Board_Project

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

Create `.env` and configure:

```env
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
ALGORITHM=HS256

MAIL_USERNAME=your_email
MAIL_PASSWORD=your_password

CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

Run migration:

```bash
alembic upgrade head
```

Start the server:

```bash
uvicorn main:app --reload
```

## 📚 API Documentation

Swagger:

```text
http://127.0.0.1:8000/docs
```



## 🐳 Docker

```bash
docker compose up --build
```

Stop:

```bash
docker compose down
```

## 🎯 Project Highlights

This project demonstrates practical backend development with:

**FastAPI • PostgreSQL • SQLAlchemy • JWT • RBAC • Alembic • Cloudinary • Docker • REST API • Email Integration**

## 👨‍💻 Author

**Jahid Alam**
Python Backend Developer

GitHub:
https://github.com/jahid6261

Project:
https://github.com/jahid6261/Job_Board_Project

---

⭐ **Built for portfolio, learning, and backend development practice.**
