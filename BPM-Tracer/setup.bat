@echo off
echo ===================================================
echo     Instalacion de dependencias BPM Tracer
echo ===================================================
echo.

echo 1. Instalando dependencias base (actualizando pip y build tools)...
python -m pip install --upgrade pip setuptools wheel cython numpy
if %errorlevel% neq 0 exit /b %errorlevel%

echo.
echo 2. Instalando madmom ignorando compatibilidades estrictas de build...
python -m pip install madmom --no-build-isolation
if %errorlevel% neq 0 exit /b %errorlevel%

echo.
echo 3. Instalando el resto de requerimientos...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 exit /b %errorlevel%

echo.
echo 4. Aplicando parche de compatibilidad para Python 3.12+ a madmom...
python patch_madmom.py
if %errorlevel% neq 0 exit /b %errorlevel%

echo.
echo !Todo listo! El entorno esta preparado.
pause
