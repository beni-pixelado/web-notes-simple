from fastapi import FastAPI, Request, HTTPException, Depends, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import sqlite3
import hashlib
import os
#python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
#para acessar web http://192.168.15.35:8000

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Inicializar banco de dados
def init_db():
    conn = sqlite3.connect("users.db")
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
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Hash de senha
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Verificar sessão
def verify_session(session_token: Optional[str] = Cookie(None)) -> str:
    if not session_token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    return session_token

# Obter user_id da sessão
def get_user_id(session_token: str) -> int:
    # Neste exemplo simples, o token é o user_id
    try:
        return int(session_token)
    except:
        raise HTTPException(status_code=401, detail="Sessão inválida")

# Modelos
class User(BaseModel):
    username: str
    email: str
    password: str

# Rotas
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, session_token: Optional[str] = Cookie(None)):
    if not session_token:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        user_id = get_user_id(session_token)
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        
        c.execute("SELECT * FROM notes WHERE user_id = ?", (user_id,))
        notes = c.fetchall()
        conn.close()
        
        if not user:
            return RedirectResponse(url="/login", status_code=302)
        
        notes_list = [{"id": n[0], "title": n[2], "content": n[3]} for n in notes]
        
        return templates.TemplateResponse("notes.html", {
            "request": request,
            "username": user[0],
            "notes": notes_list
        })
    except:
        return RedirectResponse(url="/login", status_code=302)

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
    hashed_password = hash_password(password)
    
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = c.fetchone()
    conn.close()
    
    if user:
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="session_token", value=str(user[0]), httponly=True, max_age=86400)
        return response
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Usuário ou senha inválidos"
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
            "error": "As senhas não coincidem"
        })
    
    if len(password) < 6:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "A senha deve ter no mínimo 6 caracteres"
        })
    
    hashed_password = hash_password(password)
    
    conn = sqlite3.connect("users.db")
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
            error = "Este usuário já existe"
        else:
            error = "Este email já está registrado"
        
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": error
        })

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session_token")
    return response


