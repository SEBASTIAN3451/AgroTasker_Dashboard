# Script para lanzar el servidor AgroTasker Dashboard
Write-Host "Iniciando AgroTasker Dashboard..." -ForegroundColor Green

# Actualizar PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Verificar Python
$pythonVersion = & python --version 2>&1
Write-Host "Python detectado: $pythonVersion" -ForegroundColor Cyan

# Iniciar servidor Python en segundo plano
Write-Host "`nIniciando servidor local en puerto 8080..." -ForegroundColor Yellow
$serverJob = Start-Job -ScriptBlock {
    param($workDir)
    Set-Location $workDir
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    & python server_simple.py
} -ArgumentList $PSScriptRoot

Start-Sleep -Seconds 3

# Iniciar ngrok
Write-Host "Iniciando ngrok en puerto 8080..." -ForegroundColor Yellow
& ngrok http 8080

# Cleanup cuando se cierre
Stop-Job -Job $serverJob
Remove-Job -Job $serverJob
