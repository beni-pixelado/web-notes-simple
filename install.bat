@echo off
REM Script para instalar dependências do web-notes-simple
echo ========================================
echo Instalador Web Notes Simple
echo ========================================
echo.

REM Verificar se Python está instalado
echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python nao encontrado! Instale Python 3.8+ de https://www.python.org/
    timeout /t 5
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo OK Python encontrado: %PYTHON_VERSION%
echo.

REM Criar virtual environment
echo Criando ambiente virtual...
if exist "venv\" (
    echo OK Virtual environment ja existe
) else (
    python -m venv venv
    if errorlevel 1 (
        echo X Erro ao criar virtual environment
        timeout /t 5
        exit /b 1
    )
    echo OK Virtual environment criado
)
echo.

REM Ativar virtual environment
echo Ativando virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo X Erro ao ativar virtual environment
    timeout /t 5
    exit /b 1
)
echo OK Virtual environment ativado
echo.

REM Atualizar pip
echo Atualizando pip...
python -m pip install --upgrade pip -q
echo.

REM Instalar dependências
echo Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo X Erro ao instalar dependencias
    timeout /t 5
    exit /b 1
)
echo OK Dependencias instaladas com sucesso!
echo.

echo ========================================
echo Instalacao concluida!
echo ========================================
echo.
echo Para executar o servidor, use:
echo   python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
echo.
echo Depois acesse no navegador:
echo   http://127.0.0.1:8000/register  (criar conta)
echo   http://127.0.0.1:8000/login     (fazer login)
echo.
pause
