# ProspecMan - Iniciar App Mobile (Expo)
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notmatch "^(127|169)" -and $_.PrefixOrigin -in @("Dhcp","Manual") } | Sort-Object InterfaceMetric | Select-Object -First 1).IPAddress

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  ProspecMan - App Mobile (Expo)"     -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  IP detectado : $ip" -ForegroundColor Green
Write-Host "  API URL      : http://${ip}:8000" -ForegroundColor Green
Write-Host ""
Write-Host '  1. Certifique-se de que a API esta rodando (.\start_api.ps1)' -ForegroundColor Yellow
Write-Host '  2. Instale o app Expo Go no celular' -ForegroundColor Yellow
Write-Host '  3. Escaneie o QR code que aparecera abaixo' -ForegroundColor Yellow
Write-Host ""
Write-Host '  Para mudar a URL da API: edite mobile/.env' -ForegroundColor Gray
Write-Host ""

Push-Location mobile
npx expo start --lan
Pop-Location
