# Project Structure

## Organization

```
web-notes-simple/
├── backend/
│   ├── main.py                 # Main FastAPI application file
│   ├── templates/              # HTML Templates (Jinja2)
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── notes.html
│   │   ├── create.html
│   │   ├── edit.html
│   │   └── view_note.html
│   ├── uploads/                # Folder for note image uploads
│   ├├─ .gitkeep
│   └── users.db                # SQLite database
├── frontend/
│   └── static/
│       ├── css/                # CSS files
│       │   ├── login.css
│       │   ├── register.css
│       │   └── notes.css
│       └── js/                 # JavaScript files
│           ├── create.js
│           ├── notes.js
│           └── create_color.js
├── start.sh                    # Start script (Linux/Mac)
├── start.ps1                   # Start script (PowerShell)
├── start.bat                   # Start script (CMD)
├── requirements.txt            # Python dependencies
├── README.md                   # Documentation
└── STRUCTURE.md               # This file
```

## Initialization

### Linux/Mac
```bash
bash start.sh
```

### Windows (PowerShell)
```powershell
.\start.ps1
```

### Windows (CMD)
```cmd
start.bat
```

### Manual (anywhere)
```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

## Comments on the Structure

- **Backend**: Contains the application logic, templates and data
- **Frontend**: Contains static files (CSS, JavaScript)
- **Static Files**: FastAPI mounts the `frontend/static` folder to `/static` in the application route
- **Uploads**: Note images are stored in `backend/uploads`
- **Database**: SQLite (`users.db`) is in `backend` for better organization
