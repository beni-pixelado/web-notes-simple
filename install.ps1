# Script para instalar dependências do web-notes-simple
# Execute como: powershell -ExecutionPolicy Bypass -File install.ps1

Write-Host "========================================" -ForegroundColor Green
Write-Host "Instalador Web Notes Simple" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Verificar se Python está instalado
Write-Host "Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python não encontrado! Instale Python 3.8+ de https://www.python.org/" -ForegroundColor Red
    exit 1
}

# Criar virtual environment
Write-Host "`nCriando ambiente virtual..." -ForegroundColor Yellow
if (Test-Path ".\venv") {
    Write-Host "✓ Virtual environment já existe" -ForegroundColor Green
} else {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Virtual environment criado" -ForegroundColor Green
    } else {
        Write-Host "✗ Erro ao criar virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Ativar virtual environment
Write-Host "`nAtivando virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Virtual environment ativado" -ForegroundColor Green
} else {
    Write-Host "✗ Erro ao ativar virtual environment" -ForegroundColor Red
    exit 1
}

# Atualizar pip
Write-Host "`nAtualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip -q

# Instalar dependências
Write-Host "`nInstalando dependências..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependências instaladas com sucesso!" -ForegroundColor Green
} else {
    Write-Host "✗ Erro ao instalar dependências" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Instalação concluída!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Para executar o servidor, use:" -ForegroundColor Cyan
Write-Host "  python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload" -ForegroundColor White
Write-Host ""
Write-Host "Depois acesse no navegador:" -ForegroundColor Cyan
Write-Host "  http://127.0.0.1:8000/register  (criar conta)" -ForegroundColor White
Write-Host "  http://127.0.0.1:8000/login     (fazer login)" -ForegroundColor White
Write-Host ""
