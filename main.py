from fastapi import FastAPI, Request, HTTPException, Depends, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import sqlite3
import hashlib
import os
import shutil
import time
from pathlib import Path
#python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
#acess in web: http://127.0.0.1:8000

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
templates = Jinja2Templates(directory="templates")

# Criar pasta uploads se não existir
upload_dir = Path("uploads")
upload_dir.mkdir(exist_ok=True)

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
            image_path TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Adicionar coluna image_path se não existir (para bancos de dados antigos)
    try:
        c.execute("ALTER TABLE notes ADD COLUMN image_path TEXT")
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    # Adicionar coluna text_color se não existir
    try:
        c.execute("ALTER TABLE notes ADD COLUMN text_color TEXT DEFAULT '#000000'")
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
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

# Obter username da sessão
def get_username(session_token: str) -> str:
    try:
        user_id = get_user_id(session_token)
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        conn.close()
        return user[0] if user else ""
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
        # Usar form-data para pegar todos os dados
        form_data = await request.form()
        title = form_data.get("title", "")
        content = form_data.get("content", "")
        image = form_data.get("image")
        
        image_path = None
        text_color = form_data.get("text_color") or "#000000"
        
        # Processar upload de imagem
        if image and image.filename:
            try:
                # Salvar arquivo
                file_extension = os.path.splitext(image.filename)[1]
                unique_filename = f"note_{user_id}_{int(time.time())}{file_extension}"
                file_path = f"uploads/{unique_filename}"
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                
                image_path = f"/{file_path}"
            except Exception as img_error:
                print(f"Erro ao salvar imagem: {img_error}")
                # Continuar mesmo se a imagem falhar
        
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("INSERT INTO notes (user_id, title, content, image_path, text_color) VALUES (?, ?, ?, ?, ?)", 
              (user_id, title, content, image_path, text_color))
        conn.commit()
        conn.close()

        return RedirectResponse(url="/", status_code=302)
    except Exception as e:
        print(f"Erro ao criar nota: {str(e)}")
        try:
            username = get_username(session_token) if session_token else ""
        except:
            username = ""
        return templates.TemplateResponse("create.html", {"request": request, "username": username, "error": f"Erro ao salvar a nota: {str(e)}"})


@app.get("/note/{note_id}", response_class=HTMLResponse)
async def view_note_page(request: Request, note_id: int, session_token: Optional[str] = Cookie(None)):
    if not session_token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        user_id = get_user_id(session_token)
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT id, user_id, title, content, image_path, text_color FROM notes WHERE id = ?", (note_id,))
        note = c.fetchone()
        conn.close()

        if not note:
            raise HTTPException(status_code=404, detail="Nota não encontrada")

        if note[1] != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")

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
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT user_id, image_path, text_color FROM notes WHERE id = ?", (note_id,))
        note = c.fetchone()

        if not note:
            raise HTTPException(status_code=404, detail="Nota não encontrada")

        if note[0] != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")

        # Deletar arquivo de imagem se existir
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
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT id, user_id, title, content, image_path, text_color FROM notes WHERE id = ?", (note_id,))
        note = c.fetchone()
        conn.close()

        if not note:
            raise HTTPException(status_code=404, detail="Nota não encontrada")

        if note[1] != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")

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
        # Usar form-data para pegar todos os dados
        form_data = await request.form()
        title = form_data.get("title", "")
        content = form_data.get("content", "")
        image = form_data.get("image")
        
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        
        # Verificar se a nota existe e pertence ao usuário
        c.execute("SELECT user_id, image_path FROM notes WHERE id = ?", (note_id,))
        note = c.fetchone()
        
        if not note:
            raise HTTPException(status_code=404, detail="Nota não encontrada")
        
        if note[0] != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        image_path = note[1]  # Manter imagem anterior caso não seja feito upload
        prev_text_color = note[2] if len(note) > 2 and note[2] else "#000000"
        new_text_color = form_data.get("text_color") or prev_text_color
        
        # Processar novo upload de imagem
        if image and image.filename:
            try:
                # Deletar imagem anterior se existir
                if image_path and os.path.exists(image_path[1:]):  # Remove leading /
                    os.remove(image_path[1:])
                
                # Salvar novo arquivo
                file_extension = os.path.splitext(image.filename)[1]
                unique_filename = f"note_{user_id}_{int(time.time())}{file_extension}"
                file_path = f"uploads/{unique_filename}"
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                
                image_path = f"/{file_path}"
            except Exception as img_error:
                print(f"Erro ao salvar imagem: {img_error}")
                # Continuar mesmo se a imagem falhar
        
        # Atualizar a nota (inclui text_color)
        c.execute("UPDATE notes SET title = ?, content = ?, image_path = ?, text_color = ? WHERE id = ?", 
              (title, content, image_path, new_text_color, note_id))
        conn.commit()
        conn.close()
        
        return RedirectResponse(url="/", status_code=302)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao editar nota: {str(e)}")
        return RedirectResponse(url="/", status_code=302)

