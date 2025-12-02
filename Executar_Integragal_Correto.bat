@echo off
title IntegraGAL
echo ================================================
echo           INTEGRAFAL v2.0
echo ================================================
echo.
echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python nao encontrado. Instalando dependencias...
    pip install pandas customtkinter bcrypt
    echo.
    echo Tentando executar novamente...
)

echo Iniciando IntegraGAL...
python main.py

if errorlevel 1 (
    echo.
    echo ERRO: Verifique as dependencias
    echo pip install pandas customtkinter bcrypt
)

echo.
echo Programa finalizado.
pause