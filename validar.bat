@echo off
title Validacao - IntegraGAL
echo ================================
echo   VALIDACAO DO SISTEMA v2.0
echo ================================
echo.

echo Testando autenticacao...
python -c "from autenticacao.auth_service import AuthService; auth = AuthService(); print('marcio/flafla:', 'SUCESSO' if auth.verificar_senha('marcio', 'flafla') else 'FALHOU')"

echo.
echo Testando gerenciamento...
python -c "from core.authentication.user_manager import UserManager; um = UserManager(); print('Usuarios carregados:', len(um.listar_usuarios()))"

echo.
pause