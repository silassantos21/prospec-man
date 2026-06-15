# ProspecMan - Atualiza IP nos arquivos .env
# Execute quando reconectar ao hotspot e o IP do PC mudar

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

# Atualiza mobile/.env
$mobileEnv = "mobile/.env"
Set-Content -Path $mobileEnv -Value "EXPO_PUBLIC_API_URL=http://${ip}:8000" -Encoding utf8
Write-Host "  [OK] $mobileEnv atualizado" -ForegroundColor Green

# Atualiza web/.env.local
$webEnv = "web/.env.local"
Set-Content -Path $webEnv -Value "NEXT_PUBLIC_API_URL=http://${ip}:8000" -Encoding utf8
Write-Host "  [OK] $webEnv atualizado" -ForegroundColor Green

Write-Host ""
Write-Host "  API URL: http://${ip}:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host '  Proximos passos:' -ForegroundColor Yellow
Write-Host '    1. .\start_api.ps1    (reinicie se ja estava rodando)' -ForegroundColor Yellow
Write-Host '    2. .\start_mobile.ps1 (pressione R no Expo para recarregar)' -ForegroundColor Yellow
Write-Host '    3. .\start_web.ps1    (reinicie se ja estava rodando)' -ForegroundColor Yellow
Write-Host ""
