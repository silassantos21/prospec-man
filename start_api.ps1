# ProspecMan -- Inicia o servidor API (FastAPI + uvicorn)
# Execute: .\start_api.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ProspecMan API -- Iniciando servidor" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verifica se o .venv existe
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "  ERRO: .venv nao encontrado. Execute .\setup.ps1 primeiro." -ForegroundColor Red
    exit 1
}

# Verifica se as dependencias da API estao instaladas
$uvicornCheck = & ".venv\Scripts\python.exe" -c "import uvicorn" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Instalando novas dependencias (fastapi, uvicorn)..." -ForegroundColor Yellow
    & ".venv\Scripts\pip.exe" install -r requirements.txt --quiet
    Write-Host "  OK: Dependencias atualizadas" -ForegroundColor Green
    Write-Host ""
}

# Detecta IP local (Wi-Fi ou Ethernet, exclui loopback e APIPA)
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
    $_.IPAddress -notmatch "^127\." -and $_.IPAddress -notmatch "^169\."
}).IPAddress | Select-Object -First 1

Write-Host "  Servidor iniciando em todas as interfaces (0.0.0.0:8000)" -ForegroundColor White
Write-Host ""

if ($ip) {
    Write-Host "  Acesse pelo celular (mesma rede Wi-Fi):" -ForegroundColor Yellow
    Write-Host "    API:          http://${ip}:8000" -ForegroundColor Green
    Write-Host "    Documentacao: http://${ip}:8000/docs" -ForegroundColor Green
    Write-Host "    Health check: http://${ip}:8000/api/health" -ForegroundColor Green
} else {
    Write-Host "  AVISO: IP local nao detectado." -ForegroundColor Yellow
    Write-Host "  Execute 'ipconfig' no terminal para encontrar seu IP Wi-Fi." -ForegroundColor Yellow
    Write-Host "  Substituia pelo IP e acesse: http://SEU-IP:8000/docs" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  ATENCAO: Certifique-se que a porta 8000 esta liberada no Firewall." -ForegroundColor DarkYellow
Write-Host "  Para liberar (execute como Administrador):" -ForegroundColor DarkYellow
Write-Host "    netsh advfirewall firewall add rule name=`"ProspecMan API`" dir=in action=allow protocol=TCP localport=8000" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Pressione Ctrl+C para parar o servidor." -ForegroundColor DarkGray
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Impede modo repouso enquanto a API estiver rodando
powercfg /change standby-timeout-ac 0 | Out-Null
Write-Host "  [Sleep desabilitado enquanto a API rodar]" -ForegroundColor DarkGray
Write-Host ""

try {
    & ".venv\Scripts\python.exe" -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
} finally {
    # Restaura timeout de repouso para 30 minutos ao encerrar
    powercfg /change standby-timeout-ac 30 | Out-Null
    Write-Host ""
    Write-Host "  [Sleep restaurado para 30 min]" -ForegroundColor DarkGray
}
