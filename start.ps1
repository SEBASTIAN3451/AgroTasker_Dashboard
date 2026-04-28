# AgroTasker - Script de Inicio Rápido
# Este script inicia el servidor y abre el dashboard automáticamente

Write-Host "================================" -ForegroundColor Cyan
Write-Host "🌱 AgroTasker - Inicio Rápido" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Obtener ruta del script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "📁 Carpeta: $scriptPath" -ForegroundColor Yellow
Write-Host ""

# Detener procesos Python previos
Write-Host "🔄 Limpiando procesos anteriores..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1

# Iniciar servidor
Write-Host "🚀 Iniciando servidor..." -ForegroundColor Cyan
Start-Process python -ArgumentList "server_production.py" -WindowStyle Hidden
Start-Sleep -Seconds 3

# Verificar que el servidor está corriendo
$response = try {
    Invoke-WebRequest -Uri "http://localhost:8080/" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    $true
} catch {
    $false
}

if ($response) {
    Write-Host "✓ Servidor iniciado correctamente" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Dashboards disponibles:" -ForegroundColor Green
    Write-Host "  1. Simple      → http://localhost:8080/dashboard_simple.html"
    Write-Host "  2. Avanzado    → http://localhost:8080/dashboard_advanced.html"
    Write-Host "  3. Original    → http://localhost:8080/dashboard.html"
    Write-Host "  4. Menú        → http://localhost:8080/index-menu.html"
    Write-Host ""
    Write-Host "🌐 Abriendo Dashboard Avanzado..." -ForegroundColor Cyan
    Start-Sleep -Seconds 1
    
    # Abrir en navegador
    Start-Process "http://localhost:8080/index-menu.html"
    
    Write-Host ""
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host "✓ Sistema listo para usar" -ForegroundColor Green
    Write-Host "Presiona Ctrl+C para detener" -ForegroundColor Yellow
    Write-Host "================================" -ForegroundColor Cyan
    
    # Mantener la ventana abierta
    Read-Host "Presiona Enter para cerrar esta ventana"
} else {
    Write-Host "✗ Error: No se pudo iniciar el servidor" -ForegroundColor Red
    Read-Host "Presiona Enter para cerrar"
}
