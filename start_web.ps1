# ProspecMan -- Inicia o frontend Next.js
# Execute: .\start_web.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ProspecMan Web -- Iniciando frontend" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path "web\package.json")) {
    Write-Host "  ERRO: pasta web/ nao encontrada." -ForegroundColor Red
    exit 1
}

$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
    $_.IPAddress -notmatch "^127\." -and $_.IPAddress -notmatch "^169\."
}).IPAddress | Select-Object -First 1

if ($ip) {
    Write-Host "  Acesse pelo celular (mesma rede Wi-Fi):" -ForegroundColor Yellow
    Write-Host "    http://${ip}:3000" -ForegroundColor Green
} else {
    Write-Host "  Execute 'ipconfig' para encontrar seu IP e acesse http://SEU-IP:3000" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  IMPORTANTE: a API tambem precisa estar rodando." -ForegroundColor DarkYellow
Write-Host "  Em outro terminal: .\start_api.ps1" -ForegroundColor DarkYellow
Write-Host ""
Write-Host "  Pressione Ctrl+C para parar." -ForegroundColor DarkGray
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Push-Location "web"
npm run dev:host
Pop-Location
