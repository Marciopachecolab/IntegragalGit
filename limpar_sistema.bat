@echo off
chcp 65001 >nul

echo -----------------------------------------------------
echo INICIANDO LIMPEZA DO SISTEMA INTEGRAGAL
echo -----------------------------------------------------

:: Verificar se main.py existe
if not exist "main.py" (
    echo ERRO: main.py nao encontrado. Execute este script na pasta raiz do projeto.
    pause
    exit /b 1
)

echo Diretorio correto identificado.
echo.

:: Gerar timestamp seguro (YYYYMMDD_HHMM)
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set data=%%c%%b%%a
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set hora=%%a%%b
set timestamp=%data%_%hora%
set backup_file=backup_integragal_%timestamp%.zip

echo Criando backup de seguranca...
echo (isso pode levar alguns segundos)

powershell -Command "$paths = Get-ChildItem -Recurse -File | Where-Object { $_.FullName -notmatch 'backup_.*\.zip' -and $_.Extension -ne '.zip' -and $_.FullName -notmatch '__pycache__' -and $_.Extension -ne '.pyc' -and $_.FullName -notmatch '\\analise\\' -and $_.FullName -notmatch '\\reports\\.*\.csv' } | Select-Object -ExpandProperty FullName -Unique; Compress-Archive -Path $paths -DestinationPath '%backup_file%' -Force"

echo Backup criado: %backup_file%
echo.

:: 1. Limpando cache Python
echo Limpando cache Python...
if exist "__pycache__" rmdir /s /q "__pycache__"
for /d /r . %%d in (__pycache__) do if exist "%%d" rmdir /s /q "%%d"
del /s /q *.pyc 2>nul
echo OK.
echo.

:: 2. Arquivos de correcoes (.md)
echo Removendo arquivos de correcoes (.md)...
del /q *.md ANALISE_*.md CORRECAO_*.md CORRECOES_*.md GUIA_*.md IMPLEMENTACAO_*.md PROBLEMA_*.md RELATORIO_*.md RESUMO_*.md 2>nul
echo OK.
echo.

:: 3. Arquivos de instrução (.txt)
echo Removendo arquivos de instrucao (.txt)...
del /q *.txt INSTRUCOES_*.txt 2>nul
echo OK.
echo.

:: 4. Pacotes ZIP antigos
echo Removendo pacotes ZIP antigos...
for /f %%i in ('dir /b IntegraGAL_*.zip 2^>nul') do (
    set "file=%%i"
    set "skip="
    for %%j in (IntegraGAL_TKINTER_PURO_FINAL_*.zip) do if "%%i"=="%%j" set "skip=1"
    if not defined skip del "%%i" 2>nul
)
echo OK.
echo.

:: 5. Pasta analise
if exist "analise" (
    echo Removendo pasta analise...
    rmdir /s /q "analise"
    echo OK.
    echo.
)

:: 6. Relatorios antigos
if exist "reports" (
    echo Removendo relatorios antigos...
    del /q reports\gal_*.csv 2>nul
    del /q reports\test_integration_* 2>nul
    echo OK.
    echo.
)

:: 7. Pasta tmp
if exist "tmp" (
    echo Removendo pasta tmp...
    rmdir /s /q "tmp"
    echo OK.
    echo.
)

:: 8. Arquivos texto desnecessarios
echo Removendo arquivos TXT desnecessarios...
del /q DOWNLOAD_FILES.txt LEIA_ME_ANTES_DE_USAR.txt 2>nul
echo OK.
echo.

:: 9. Logs antigos
echo Removendo logs antigos...
del /q *.log 2>nul
echo OK.
echo.

echo -----------------------------------------------------
echo ESTATISTICAS FINAIS
echo -----------------------------------------------------

for /f %%i in ('dir /s /b /a-d 2^>nul ^| find /c /v ""') do set total_arquivos=%%i
for /f %%i in ('dir /s /b /ad 2^>nul ^| find /c /v ""') do set dirs_restantes=%%i

echo Arquivos restantes: %total_arquivos%
echo Pastas restantes: %dirs_restantes%
echo.

echo ESTRUTURA FINAL DO PROJETO:
echo -----------------------------------------------------
dir /b | more

echo.
echo LIMPEZA CONCLUIDA COM SUCESSO.
echo -----------------------------------------------------
echo - Execute: python main.py para testar
echo - Verifique autenticacao e exports
echo - Mantenha o arquivo: %backup_file%
echo -----------------------------------------------------
pause
