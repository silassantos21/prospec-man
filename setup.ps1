# ProspecMan -- Script de instalacao (Windows PowerShell)
# Execute: .\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ProspecMan -- Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verifica Python
Write-Host "[1/5] Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  OK: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERRO: Python nao encontrado. Instale em https://python.org" -ForegroundColor Red
    exit 1
}

# 2. Cria ambiente virtual
Write-Host "[2/5] Criando ambiente virtual (.venv)..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "  OK: .venv criado" -ForegroundColor Green
} else {
    Write-Host "  OK: .venv ja existe" -ForegroundColor Green
}

# 3. Instala dependencias
Write-Host "[3/5] Instalando dependencias..." -ForegroundColor Yellow
& ".venv\Scripts\pip.exe" install --upgrade pip --quiet
& ".venv\Scripts\pip.exe" install -r requirements.txt --quiet
Write-Host "  OK: Dependencias instaladas" -ForegroundColor Green

# 4. Cria .env a partir do exemplo
Write-Host "[4/5] Configurando variaveis de ambiente..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  OK: .env criado. Edite o arquivo com suas chaves de API!" -ForegroundColor Yellow
} else {
    Write-Host "  OK: .env ja existe" -ForegroundColor Green
}

# 5. Cria pasta de projetos
Write-Host "[5/5] Criando pasta de saida (projects/)..." -ForegroundColor Yellow
if (-not (Test-Path "projects")) {
    New-Item -ItemType Directory -Path "projects" | Out-Null
}
Write-Host "  OK: projects/ pronta" -ForegroundColor Green

# Resultado
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Setup concluido!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "PROXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. Edite o arquivo .env com suas chaves:" -ForegroundColor White
Write-Host "     ANTHROPIC_API_KEY=sk-ant-..."
Write-Host "     GROQ_API_KEY=gsk_..."
Write-Host ""
Write-Host "  2. Ative o ambiente virtual:" -ForegroundColor White
Write-Host "     .venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "  3. Execute o ProspecMan:" -ForegroundColor White
Write-Host "     python main.py run --audio briefing.mp3"
Write-Host ""
Write-Host "  Onde obter as chaves:" -ForegroundColor Cyan
Write-Host "  - Anthropic: https://console.anthropic.com"
Write-Host "  - Groq:      https://console.groq.com"
Write-Host ""
