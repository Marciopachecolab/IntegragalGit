@echo off
echo ========================================
echo          IntegraGAL v2.0
echo    Sistema de Gestao de Exames
echo ========================================
echo.
echo Iniciando sistema...
echo.

cd /d "%~dp0"
python main.py

if errorlevel 1 (
    echo.
    echo Erro ao executar o sistema!
    echo Verifique se o Python esta instalado.
    pause
)
