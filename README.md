(these project are in portuguese)

# Web Notes Simple

Aplicação web para criar, editar e gerenciar notas pessoais com suporte a imagens e diversas outras funcionalidades.

## Requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## Instalação Rápida

### Option 1: Script Automático (Recomendado)

#### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

#### Windows (CMD)
```cmd
install.bat
```

Estes scripts vão:
1. ✓ Verificar se Python está instalado
2. ✓ Criar um ambiente virtual (venv)
3. ✓ Instalar todas as dependências
4. ✓ Exibir instruções para executar

### Option 2: Instalação Manual

1. **Criar ambiente virtual:**
```bash
python -m venv venv
```

2. **Ativar ambiente virtual:**

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

3. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

## Executar o Servidor

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Depois acesse no navegador:
- **Criar Conta:** http://127.0.0.1:8000/register
- **Fazer Login:** http://127.0.0.1:8000/login

## Estrutura do Projeto

```
web-notes-simple/
├── main.py                 # Aplicação FastAPI principal
├── requirements.txt        # Dependências Python
├── install.ps1            # Script de instalação (PowerShell)
├── install.bat            # Script de instalação (CMD)
├── templates/             # Arquivos HTML
│   ├── create.html       # Página para criar nota
│   ├── edit.html         # Página para editar nota
│   ├── login.html        # Página de login
│   ├── register.html     # Página de registro
│   ├── notes.html        # Página inicial
│   └── view_note.html    # Página para ver nota
├── static/               # Arquivos estáticos
│   ├── css/
│   │   ├── notes.css     # Estilos principais
│   │   ├── login.css     # Estilos de login
│   │   └── register.css  # Estilos de registration
│   └── js/
│       ├── create_color.js # Lógica de seletor de cores
│       ├── create.js      # Scripts para criar nota
│       └── notes.js       # Scripts gerais
├── uploads/              # Pasta para imagens de notas
└── users.db             # Banco de dados SQLite

```

## Dependências

- **fastapi** - Framework web moderno
- **uvicorn** - Servidor ASGI
- **jinja2** - Engine de templates
- **pydantic** - Validação de dados
- **python-multipart** - Suporte para upload de arquivos

## Recursos

✓ Criar, editar e deletar notas
✓ Upload de imagens para notas
✓ Customizar cor do texto
✓ Autenticação de usuário
✓ Banco de dados SQLite
✓ Interface responsiva

## Notas de Desenvolvimento

- O banco de dados é criado automaticamente na primeira execução
- As quatro senhas são salvas com hash SHA-256
- As imagens uploadadas ficam na pasta `uploads/`
- Use `--reload` para desenvolvimento (recarrega a cada mudança)

## Solução de Problemas

**Erro: "Python não encontrado"**
- Instale Python de https://www.python.org/
- Certifique-se de que está no PATH do Windows

**Erro: "Porta 8000 já em uso"**
- Use outra porta: `--port 8001`
- Ou encerre o processo usando a porta 8000

**Virtual environment não ativa**
- Certifique-se de executar o comando de ativação correto para seu SO
- No PowerShell, pode ser necessário alterar a política de execução

## Licença

Este projeto é fornecido como está, sem garantias.
