# 🐶 Dog Profile & Record Database (Flask App)

A web application for managing dog profiles, documents, and communication in a shelter or foster environment.

This project started as a simple Flask + SQLite demo and has been expanded into a more complete system with authentication, file uploads, and role-based access.

---

## 🚀 Features

- 🐕 Dog profile management (create, edit, delete)
- 🔍 Search and filtering (name, size, status)
- 📄 Document uploads (vet records, intake forms, etc.)
- 💬 Per-dog chat / notes system
- 🔐 User authentication (login/register)
- 🧑‍⚖️ Role-based permissions:
  - Admin
  - Coordinator
  - Staff
  - Foster
- 🗂 Organized project structure (routes + services)
- ☁️ Ready for cloud storage (Cloudinary / S3)
- 🧪 SQLite (local) or PostgreSQL (production-ready)

---

## 🛠 Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite (dev) / PostgreSQL (optional)
- **ORM:** SQLAlchemy
- **Auth:** Session-based authentication
- **Storage:** Local (dev) + Cloudinary-ready
- **Frontend:** HTML + CSS (custom)

---

## ⚙️ Quickstart

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd dog_profile_demo
