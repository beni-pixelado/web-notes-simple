![License: MIT](https://img.shields.io/badge/License-MIT-FFD700?style=for-the-badge)
# Web Notes Simple

<img width="1366" height="768" alt="Captura de tela 2026-02-19 180534" src="https://github.com/user-attachments/assets/bb2acbcc-ef68-4591-a771-713cf5d9d942" />

![Version 1.0.0](https://img.shields.io/badge/V1.0.0-FFD700?style=for-the-badge&logoColor=black)  ![Stars](https://img.shields.io/github/stars/beni-pixelado/web-notes-simple?style=for-the-badge&color=FFD700)

Web application to create, edit and manage personal notes with image support and various other features.

## Requirements

- Python 3.8+
- pip (Python package manager)

## Quick Installation

### Option 1: Automatic Script (Recommended)

#### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

#### Windows (CMD)
```cmd
install.bat
```

These scripts will:
1. ✓ Check if Python is installed
2. ✓ Create a virtual environment (venv)
3. ✓ Install all dependencies
4. ✓ Display instructions to run

### Option 2: Manual Installation

1. **Create virtual environment:**
```bash
python -m venv venv
```

2. **Activate virtual environment:**

Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```

Windows (CMD):
```cmd
venv\Scripts\activate.bat
```

Linux/Mac:
```bash
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Run the Server

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
or acess "start.xxx"

Then access in the browser **http://127.0.0.1:8000**

**structure in STRUCTURE.md**

## Dependencies

- **fastapi** - Modern web framework
- **uvicorn** - ASGI server
- **jinja2** - Template engine
- **pydantic** - Data validation
- **python-multipart** - File upload support

## Features

✓ Create, edit and delete notes
✓ Upload images for notes
✓ Customize text color
✓ User authentication
✓ SQLite database
✓ Responsive interface

## Development Notes

- The database is created automatically on first run
- Passwords are saved with SHA-256 hash
- Uploaded images are stored in the `uploads/` folder
- Use `--reload` for development (reloads on each change)

## Troubleshooting

**Error: "Python not found"**
- Install Python from https://www.python.org/
- Make sure it's in the Windows PATH

**Error: "Port 8000 already in use"**
- Use another port: `--port 8001`
- Or terminate the process using port 8000

**Virtual environment not active**
- Make sure to run the correct activation command for your OS
- In PowerShell, you may need to change the execution policy

## License

This project is provided as is, without warranties.
