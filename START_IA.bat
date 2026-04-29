@echo off
REM ============================================
REM AgroTasker - Script de Arranque Automatico
REM Sistema IA con Transformer
REM ============================================
setlocal enabledelayedexpansion

echo.
echo ====================================================
echo   AgroTasker - Sistema IA con Transformer
echo   Predicciones + Semaforizacion + Alarmas
echo ====================================================
echo.

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM ============================================
REM PASO 1: Verificar/Crear Virtual Environment
REM ============================================
echo [1/5] Verificando entorno virtual...
set "VENV_DIR=venv"
if exist ".venv\Scripts\activate.bat" set "VENV_DIR=.venv"

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo   Creando entorno virtual en %VENV_DIR%...
    python -m venv "%VENV_DIR%"
    if !errorlevel! neq 0 (
        echo   Error creando entorno virtual. Asegurate de tener Python instalado.
        pause
        exit /b 1
    )
) else (
    echo   Entorno virtual encontrado: %VENV_DIR%
)

call "%VENV_DIR%\Scripts\activate.bat"
if !errorlevel! neq 0 (
    echo   Error activando entorno virtual.
    pause
    exit /b 1
)
echo   Entorno virtual activado.

REM ============================================
REM PASO 2: Instalar Dependencias
REM ============================================
echo.
echo [2/5] Instalando dependencias...
pip install -q -r requirements.txt
if !errorlevel! neq 0 (
    echo   Error instalando dependencias.
    pause
    exit /b 1
)
echo   Dependencias instaladas.

REM ============================================
REM PASO 3: Verificar/Entrenar Modelo
REM ============================================
echo.
echo [3/5] Verificando modelos Transformer...

if not exist "models\" mkdir models

set "MODELS_OK=1"
if not exist "models\transformer_field1.h5" set "MODELS_OK=0"
if not exist "models\transformer_field2.h5" set "MODELS_OK=0"
if not exist "models\transformer_field3.h5" set "MODELS_OK=0"
if not exist "models\transformer_field4.h5" set "MODELS_OK=0"
if not exist "models\scalers.pkl" set "MODELS_OK=0"

if "%MODELS_OK%"=="0" (
    echo   Modelos incompletos. Entrenando Transformer...
    echo   Esto puede tomar 3-7 minutos.
    echo.
    python predictions_model.py train
    if !errorlevel! neq 0 (
        echo   Error durante el entrenamiento.
        pause
        exit /b 1
    )
    echo   Modelos Transformer entrenados.
) else (
    echo   Modelos Transformer encontrados.
)

REM ============================================
REM PASO 4: Iniciar Servidor Flask
REM ============================================
echo.
echo [4/5] Iniciando servidor Flask en puerto 5000...
echo   El dashboard quedara disponible en http://localhost:5000
echo.

start "Servidor AgroTasker IA" cmd /k ""cd /d "%SCRIPT_DIR%" && call "%VENV_DIR%\Scripts\activate.bat" && python predictions_server.py""

timeout /t 3 /nobreak

REM ============================================
REM PASO 5: Abrir Dashboard
REM ============================================
echo.
echo [5/5] Abriendo dashboard...
start "" "http://localhost:5000" 2>nul || (
    echo   Abre manualmente en tu navegador:
    echo   http://localhost:5000
)

echo.
echo ====================================================
echo   Sistema iniciado correctamente
echo ====================================================
echo   Dashboard:     http://localhost:5000
echo   API Server:    http://localhost:5000/api
echo   Predicciones:  http://localhost:5000/api/predictions
echo   Alarmas:       http://localhost:5000/api/alarms
echo.
echo Para detenerlo, cierra la ventana del servidor o presiona Ctrl+C ahi.
echo.
pause
