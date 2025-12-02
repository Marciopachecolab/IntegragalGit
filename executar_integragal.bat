@echo off
chcp 65001 >nul
title IntegraGAL - Sistema de Análise Laboratorial

echo ================================================
echo           INTEGRAFAL v2.0 - WINDOWS
echo ================================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python não encontrado no PATH
    echo Por favor, instale Python 3.8+ e adicione ao PATH
    pause
    exit /b 1
)

REM Vai para o diretório do script
cd /d "%~dp0"

REM Verifica se existe o diretório IntegragalGit
if not exist "IntegragalGit" (
    echo ERRO: Diretório IntegragalGit não encontrado
    echo Certifique-se de estar executando do diretório correto
    pause
    exit /b 1
)

echo Iniciando IntegraGAL...
echo Diretório atual: %CD%
echo.

REM Executa o programa
python IntegragalGit/main.py

REM Se chegou aqui, o programa fechou
echo.
echo Programa finalizado.
pause
