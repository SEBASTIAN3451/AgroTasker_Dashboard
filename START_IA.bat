@echo off
REM ====================================================
REM AGROTASKER - Script de Inicio Completo
REM Configura predicciones, alarmas y dashboard
REM ====================================================

setlocal enabledelayedexpansion

echo.
echo ====================================================
echo  AGROTASKER - Sistema Completo de IA
echo ====================================================
echo.

REM Verificar si está en el directorio correcto
if not exist "predictions_model.py" (
    echo Error: Este script debe ejecutarse desde c:\Users\SEBASTIAN\AgroTasker_Dashboard
    pause
    exit /b 1
)

REM Activar virtual environment si existe
if exist "venv\Scripts\activate.bat" (
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
)

REM Instalar dependencias
echo.
echo [1/4] Instalando dependencias...
echo.
pip install -q -r requirements.txt 2>nul
if !ERRORLEVEL! neq 0 (
    echo Error instalando dependencias
    pause
    exit /b 1
)
echo ✓ Dependencias instaladas

REM Verificar si modelo existe
echo.
echo [2/4] Verificando modelos entrenados...
echo.
if exist "models\metadata.json" (
    echo ✓ Modelos encontrados
    set MODEL_STATUS=Usando modelos entrenados
) else (
    echo ⚠️  Modelos no encontrados
    echo.
    echo ¿Desea entrenar ahora? (S/N)
    set /p TRAIN_CHOICE=
    
    if /i "!TRAIN_CHOICE!"=="S" (
        echo.
        echo Entrenando modelo GRU (esto puede tomar 2-5 minutos)...
        echo.
        python predictions_model.py train
        if !ERRORLEVEL! neq 0 (
            echo Error durante entrenamiento
            pause
            exit /b 1
        )
        echo ✓ Entrenamiento completado
        set MODEL_STATUS=Modelos recién entrenados
    ) else (
        echo ⚠️  Usando datos demo (sin predicciones reales)
        set MODEL_STATUS=Datos demo
    )
)

REM Instalar versión estable del servidor de predicciones si es necesario
echo.
echo [3/4] Iniciando servidor de predicciones...
echo.
echo Abriendo terminal para servidor en puerto 5000...

REM Abrir el servidor en otra ventana
start "Servidor de Predicciones" cmd /k "title Servidor de Predicciones & python predictions_server.py"

timeout /t 3

REM Abrir dashboard
echo.
echo [4/4] Abriendo dashboard en navegador...
echo.

REM Intentar abrir el dashboard
if exist "dashboard_ia.html" (
    start "" "file:///c:/Users/SEBASTIAN/AgroTasker_Dashboard/dashboard_ia.html"
    echo ✓ Dashboard abierto
) else (
    echo Error: dashboard_ia.html no encontrado
    pause
    exit /b 1
)

echo.
echo ====================================================
echo  ✓ SISTEMA INICIADO CORRECTAMENTE
echo ====================================================
echo.
echo 📊 Dashboard: file:///c:/Users/SEBASTIAN/AgroTasker_Dashboard/dashboard_ia.html
echo 🤖 Servidor IA: http://localhost:5000
echo 📈 Predicciones: http://localhost:5000/api/predictions
echo 🚨 Alarmas: http://localhost:5000/api/alarms
echo 🚦 Semáforo: http://localhost:5000/api/traffic-light
echo.
echo Estado modelos: %MODEL_STATUS%
echo.
echo Presione cualquier tecla para continuar...
pause

echo.
echo ====================================================
echo  INFORMACIÓN DE CONTROL
echo ====================================================
echo.
echo Para cerrar el servidor:
echo   1. Cierre la ventana del Servidor de Predicciones
echo   2. O presione Ctrl+C en esa ventana
echo.
echo Para entrenar nuevo modelo:
echo   python predictions_model.py train
echo.
echo Para ver predicciones desde línea de comandos:
echo   python predictions_model.py
echo.
echo Para verificar estado del servidor:
echo   http://localhost:5000/api/health
echo.
echo Presione Ctrl+C para terminar este script
pause
