# ProspecMan - Atualiza IP no web/.env.local
# Mobile agora usa Render (nuvem) — apenas o web app precisa do IP local

$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
    $_.IPAddress -notmatch "^(127|169)" -and $_.PrefixOrigin -in @("Dhcp", "Manual")
} | Sort-Object InterfaceMetric | Select-Object -First 1).IPAddress

if (-not $ip) {
    Write-Host ""
    Write-Host "  ERRO: IP local nao detectado." -ForegroundColor Red
    Write-Host "  Conecte ao hotspot do celular e tente novamente." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  ProspecMan - Atualizando IP"         -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  IP detectado: $ip" -ForegroundColor Green
Write-Host ""

# Atualiza web/.env.local (web app usa API local)
$webEnv = "web/.env.local"
Set-Content -Path $webEnv -Value "NEXT_PUBLIC_API_URL=http://${ip}:8000" -Encoding utf8
Write-Host "  [OK] $webEnv atualizado" -ForegroundColor Green

# Mobile usa Render — nao alterar
Write-Host "  [--] mobile/.env nao alterado (usa Render)" -ForegroundColor DarkGray

Write-Host ""
Write-Host "  Web API URL: http://${ip}:8000" -ForegroundColor Cyan
Write-Host "  Mobile API URL: https://prospec-man.onrender.com (Render)" -ForegroundColor Cyan
Write-Host ""
Write-Host '  Proximos passos:' -ForegroundColor Yellow
Write-Host '    1. .\start_api.ps1    (reinicie se ja estava rodando)' -ForegroundColor Yellow
Write-Host '    2. .\start_web.ps1    (reinicie se ja estava rodando)' -ForegroundColor Yellow
Write-Host '    3. .\start_mobile.ps1 (nao precisa do start_api para o mobile)' -ForegroundColor Yellow
Write-Host ""
