@echo off
echo.
echo ============================================================
echo   THYONI TECH - SMART EDGE HUB (Distributed Edition)
echo ============================================================
echo.

:: ==========================================
:: CONFIGURACION CENTRALIZADA
:: ==========================================

:: 1. IP del servidor Nameserver (tu PC)
:: Usa "localhost" si ejecutas todo en la misma PC
:: Usa tu IP real (ej: 192.168.1.15) si usas varias PCs
set SERVER_IP=localhost

:: 2. IP de la Cámara (IP Webcam en el celular)
set CAMERA_IP=192.168.18.14

:: 3. Google Gemini API Key
set GEMINI_API_KEY=AIzaSyCPnxuKMp5pzkhCxYfNjnrCpwCNj-PnVxo

:: 4. Ruta de Python
set PYTHON_EXE="%LocalAppData%\Programs\Python\Python312\python.exe"

:: ==========================================

echo [OK] Configuración cargada:
echo      - IP Servidor: %SERVER_IP%
echo      - IP Cámara:   %CAMERA_IP%
echo.
echo   1. PRUEBA RAPIDA (sin camara real)
echo   2. CAMARA REAL (IP Webcam)
echo.
set /p MODO=Elige (1 o 2): 
echo.
echo Iniciando arquitectura distribuida...
echo.

:: Compartir variables con los procesos hijos
set EDGE_SERVER_IP=%SERVER_IP%
set EDGE_CAMERA_IP=%CAMERA_IP%

echo [1/4] Nameserver...
start "1-NS" cmd /k "cd /d "%~dp0servers" & %PYTHON_EXE% nameserver.py"
timeout /t 3 /nobreak >nul

echo [2/4] Processing Server...
start "2-PROC" cmd /k "cd /d "%~dp0servers" & %PYTHON_EXE% processing_server.py"
timeout /t 2 /nobreak >nul

echo [3/4] AI Server...
start "3-AI" cmd /k "cd /d "%~dp0servers" & %PYTHON_EXE% ai_server.py"
timeout /t 3 /nobreak >nul

if "%MODO%"=="2" (
    echo [4/4] Cliente Camara...
    start "4-CAM" cmd /k "cd /d "%~dp0client" & %PYTHON_EXE% client.py"
) else (
    echo [4/4] Cliente Prueba...
    start "4-TEST" cmd /k "cd /d "%~dp0client" & %PYTHON_EXE% test_client.py"
)

echo.
echo ============================================================
echo   [OK] Sistema distribuido en marcha
echo ============================================================
pause
