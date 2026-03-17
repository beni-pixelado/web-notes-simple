from fastapi import FastAPI, Request, HTTPException, Depends, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from passlib.context import CryptContext
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import sqlite3
import os
import shutil
import time
from pathlib import Path
#python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
#access in web: http://0.0.0.0:8000

app = FastAPI()
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../frontend/static")), name="static")
app.mount("/uploads", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "uploads")), name="uploads")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "users.db")

# Create uploads folder if it doesn't exist
upload_dir = Path("uploads")
upload_dir.mkdir(exist_ok=True)

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            image_path TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Add image_path column if it doesn't exist (for old databases)
    try:
        c.execute("ALTER TABLE notes ADD COLUMN image_path TEXT")
    except sqlite3.OperationalError:
        # Column already exists
        pass
    # Add text_color column if it doesn't exist
    try:
        c.execute("ALTER TABLE notes ADD COLUMN text_color TEXT DEFAULT '#000000'")
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    conn.commit()
    conn.close()

init_db()

# Password hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password.encode("utf-8")[:72])

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password.encode("utf-8")[:72], hashed_password)

# Verify session
def verify_session(session_token: Optional[str] = Cookie(None)) -> str:
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return session_token

# Get user_id from session
def get_user_id(session_token: str) -> int:
    # In this simple example, the token is the user_id
    try:
        return int(session_token)
    except:
        raise HTTPException(status_code=401, detail="Invalid session")

# Get username from session
def get_username(session_token: str) -> str:
    try:
        user_id = get_user_id(session_token)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        conn.close()
        return user[0] if user else ""
    except:
        raise HTTPException(status_code=401, detail="Invalid session")

# Models
class User(BaseModel):
    username: str
    email: str
    password: str

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, session_token: Optional[str] = Cookie(None)):
    if not session_token:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        user_id = get_user_id(session_token)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        
        c.execute("SELECT * FROM notes WHERE user_id = ?", (user_id,))
        notes = c.fetchall()
        conn.close()

        if not user:
            return RedirectResponse(url="/login", status_code=302)

        notes_list = []
        for n in notes:
            image_path = n[4] if len(n) > 4 else None
            text_color = n[5] if len(n) > 5 and n[5] else "#000000"
            notes_list.append({"id": n[0], "title": n[2], "content": n[3], "image_path": image_path, "text_color": text_color})
        
        return templates.TemplateResponse("notes.html", {
            "request": request,
            "username": user[0],
            "notes": notes_list
        })
    except:
        return RedirectResponse(url="/login", status_code=302)
        response.delete_cookie("session_token")
        return response 

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, session_token: Optional[str] = Cookie(None)):
    if session_token:
        try:
            user_id = get_user_id(session_token)
            return RedirectResponse(url="/", status_code=302)
        except:
            pass
    
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, username: str = Form(), password: str = Form()):
    # Conecta no banco
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()

    # Verifica se o usuário existe e se a senha confere
    if user and verify_password(password, user[1]):
        user_id = user[0]
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="session_token", value=str(user_id), httponly=True, max_age=86400)
        return response
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid username or password"
        })

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, session_token: Optional[str] = Cookie(None)):
    if session_token:
        try:
            user_id = get_user_id(session_token)
            return RedirectResponse(url="/", status_code=302)
        except:
            pass
    
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register_post(request: Request, username: str = Form(), email: str = Form(), password: str = Form(), password_confirm: str = Form()):
    if password != password_confirm:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Passwords do not match"
        })
    
    if len(password) < 6:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Password must be at least 6 characters"
        })
    
    hashed_password = hash_password(password)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                  (username, email, hashed_password))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="session_token", value=str(user_id), httponly=True, max_age=86400)
        return response
    except sqlite3.IntegrityError as e:
        conn.close()
        if "username" in str(e):
            error = "This user already exists"
        else:
            error = "This email is already registered"
        
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": error
        })

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session_token")
    return response

@app.get("/create", response_class=HTMLResponse)
async def create_note_page(request: Request, session_token: Optional[str] = Cookie(None)):
    if not session_token:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        user_id = get_user_id(session_token)
        return templates.TemplateResponse("create.html", {"request": request, "username": get_username(session_token)})
    except:
        return RedirectResponse(url="/login", status_code=302)


@app.post("/create", response_class=HTMLResponse)
async def create_note_post(request: Request, session_token: Optional[str] = Cookie(None)):
    if not session_token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        user_id = get_user_id(session_token)
        # Use form-data to get all data
        form_data = await request.form()
        title = form_data.get("title", "")
        content = form_data.get("content", "")
        image = form_data.get("image")
        
        image_path = None
        text_color = form_data.get("text_color") or "#000000"
        
        # Process image upload
        if image and image.filename:

            if not image.filename.lower().endswith((".png", ".jpg", ".jpeg")):
               return templates.TemplateResponse("create.html", {
            "request": request,
            "username": get_username(session_token),
            "error": "Only PNG, JPG and JPEG files are allowed"
            })

            try:
                # Save file
                file_extension = os.path.splitext(image.filename)[1]
                unique_filename = f"note_{user_id}_{int(time.time())}{file_extension}"
                file_path = f"uploads/{unique_filename}"
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                
                image_path = f"/{file_path}"
            except Exception as img_error:
                print(f"Error saving image: {img_error}")
                # Continue even if image fails
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO notes (user_id, title, content, image_path, text_color) VALUES (?, ?, ?, ?, ?)", 
              (user_id, title, content, image_path, text_color))
        conn.commit()
        conn.close()

        return RedirectResponse(url="/", status_code=302)
    except Exception as e:
        print(f"Error creating note: {str(e)}")
        try:
            username = get_username(session_token) if session_token else ""
        except:
            username = ""
        return templates.TemplateResponse("create.html", {"request": request, "username": username, "error": f"Error saving note: {str(e)}"})


@app.get("/note/{note_id}", response_class=HTMLResponse)
async def view_note_page(request: Request, note_id: int, session_token: Optional[str] = Cookie(None)):
    if not session_token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        user_id = get_user_id(session_token)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, user_id, title, content, image_path, text_color FROM notes WHERE id = ?", (note_id,))
        note = c.fetchone()
        conn.close()

        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

        if note[1] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        note_dict = {"id": note[0], "title": note[2], "content": note[3], "image_path": note[4], "text_color": note[5] if len(note) > 5 and note[5] else "#000000"}

        return templates.TemplateResponse("view_note.html", {"request": request, "username": get_username(session_token), "note": note_dict})
    except HTTPException:
        raise
    except Exception:
        return RedirectResponse(url="/", status_code=302)

@app.get("/delete/{note_id}")
async def delete_note(note_id: int, session_token: Optional[str] = Cookie(None)):
    if not session_token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        user_id = get_user_id(session_token)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id, image_path, text_color FROM notes WHERE id = ?", (note_id,))
        note = c.fetchone()

        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

        if note[0] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Delete image file if exists
        if note[1] and os.path.exists(note[1][1:]):  # Remove leading /
            os.remove(note[1][1:])

        c.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        conn.close()

        return RedirectResponse(url="/", status_code=302)
    except HTTPException:
        raise
    except Exception:
        return RedirectResponse(url="/", status_code=302)

@app.get("/edit/{note_id}", response_class=HTMLResponse)
async def edit_note_page(request: Request, note_id: int, session_token: Optional[str
] = Cookie(None)):
    if not session_token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        user_id = get_user_id(session_token)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, user_id, title, content, image_path, text_color FROM notes WHERE id = ?", (note_id,))
        note = c.fetchone()
        conn.close()

        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

        if note[1] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        note_dict = {"id": note[0], "title": note[2], "content": note[3], "image_path": note[4], "text_color": note[5] if len(note) > 5 and note[5] else "#000000"}

        return templates.TemplateResponse("edit.html", {"request": request, "username": get_username(session_token), "note": note_dict})
    except HTTPException:
        raise
    except Exception:
        return RedirectResponse(url="/", status_code=302)

@app.post("/edit/{note_id}")
async def edit_note_post(request: Request, note_id: int, session_token: Optional[str] = Cookie(None)):
    if not session_token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        user_id = get_user_id(session_token)
        # Use form-data to get all data
        form_data = await request.form()
        title = form_data.get("title", "")
        content = form_data.get("content", "")
        image = form_data.get("image")
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Check if the note exists and belongs to the user
        c.execute("SELECT user_id, image_path FROM notes WHERE id = ?", (note_id,))
        note = c.fetchone()
        
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        if note[0] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        image_path = note[1]  # Keep previous image if no upload
        prev_text_color = note[2] if len(note) > 2 and note[2] else "#000000"
        new_text_color = form_data.get("text_color") or prev_text_color
        
        # Process new image upload
        if image and image.filename:
            try:
                # Delete previous image if exists
                if image_path and os.path.exists(image_path[1:]):  # Remove leading /
                    os.remove(image_path[1:])
                
                # Save new file
                file_extension = os.path.splitext(image.filename)[1]
                unique_filename = f"note_{user_id}_{int(time.time())}{file_extension}"
                file_path = f"uploads/{unique_filename}"
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                
                image_path = f"/{file_path}"
            except Exception as img_error:
                print(f"Error saving image: {img_error}")
                # Continue even if image fails
        
        # Update the note (includes text_color)
        c.execute("UPDATE notes SET title = ?, content = ?, image_path = ?, text_color = ? WHERE id = ?", 
              (title, content, image_path, new_text_color, note_id))
        conn.commit()
        conn.close()
        
        return RedirectResponse(url="/", status_code=302)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error editing note: {str(e)}")
        return RedirectResponse(url="/", status_code=302)

