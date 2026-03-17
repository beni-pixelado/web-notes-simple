![License: MIT](https://img.shields.io/badge/License-MIT-FFD700?style=for-the-badge)
# 📝 Web Notes Simple

<img width="1366" height="768" alt="preview" src="https://github.com/user-attachments/assets/bb2acbcc-ef68-4591-a771-713cf5d9d942" />

![Version 1.2.0](https://img.shields.io/badge/V1.2.0-FFD700?style=for-the-badge&logoColor=black)
![Stars](https://img.shields.io/github/stars/beni-pixelado/web-notes-simple?style=for-the-badge&color=FFD700)

A simple and modern web application to create, edit and manage personal notes — now with improved architecture, security and development environment.

---

## 🚀 What's New (v1.2.0)

- 🏗️ Improved project structure and organization  
- 🔐 Password hashing with **bcrypt (passlib)**  
- 🍪 Secure session cookies (HTTP-only + expiration)  
- 🖼️ Image upload validation (basic protection)  
- 🐳 Docker support added  
- 🧪 Devcontainer configured for consistent development  
- 🛠️ Makefile for easier commands  
- ⚙️ Environment configuration support (`.env`)  

---

## ⚙️ Requirements

- Python 3.8+
- pip
- (Optional) Docker

---

## ⚡ Quick Start (Recommended)

This project includes a fully configured development environment.

### 🧪 Option 1: Devcontainer (Best Experience)

1. Open the project in VS Code  
2. Reopen in container when prompted  

✅ All dependencies and tools are automatically installed  

### 🐳 Option 2: Docker

```bash
make docker-build
make docker-run
```
### Option 3: Manual (optional)

Only needed if you are not using Devcontainer or Docker:

pip install -r requirements.txt
python -m uvicorn backend.main:app --reload

## To run the project

Only need run in terminal
``` bash
make run
```
or
``` bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔐 Security

Passwords hashed using bcrypt

Session stored in HTTP-only cookies

Basic authentication system

Route protection (login required)

Users can only access their own notes

Basic image upload validation

## ✨ Features

✓ Create, edit and delete notes
✓ Upload images for notes
✓ Custom text color
✓ User authentication (register/login/logout)
✓ SQLite database (auto-created)
✓ Protected user data
✓ Responsive interface

### 📁 Project Notes

Database is automatically created on first run

Images are stored in /uploads

Static files served via FastAPI

Uses Jinja2 templates

🧠 Future Improvements

🔐 Replace session system with secure tokens

🗄️ Migrate to PostgreSQL

🧪 Add automated tests

🔍 Search and pagination

📡 REST API

🛠️ Useful Commands
make run
make install
make docker-build
make docker-run
make clean
⚠️ Troubleshooting

Port already in use

--port 8001

Python not found

Install from https://www.python.org/

Virtual environment issues

Check activation command

📄 License

This project is provided as is, without warranties.
