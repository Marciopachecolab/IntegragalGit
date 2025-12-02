@echo off
echo ======================================
echo     IntegraGAL - Sistema de QPCR
echo ======================================
echo.

cd /d "%~dp0"

echo Verificando estrutura de arquivos...
if not exist "main.py" (
    echo ❌ main.py não encontrado!
    echo.
    echo Verifique se o package foi extraído corretamente em:
    echo %cd%
    echo.
    pause
    exit /b 1
)

echo ✅ Arquivos principais encontrados
echo.
echo Iniciando sistema...
echo.

python main.py

echo.
echo Sistema finalizado.
echo.
pause