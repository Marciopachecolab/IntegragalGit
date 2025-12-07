# Guia de Execu√ß√£o para C:\Users\marci\Downloads\Integragal

## üéØ Problema Identificado
O sistema IntegraGAL est√° sendo executado em `C:\Users\marci\Downloads\Integragal` (n√£o em `IntegragalGit`), ent√£o os caminhos precisam ser corrigidos.

## ‚úÖ Solu√ß√£o: Script de Corre√ß√£o Autom√°tica

### 1. Executar o Script de Corre√ß√£o
```bash
# Navegar para a pasta do sistema
cd C:\Users\marci\Downloads\Integragal

# Executar o script de corre√ß√£o
python corrigir_caminhos_integragal.py
```

### 2. O que o script faz:
- ‚úÖ Detecta automaticamente se √© estrutura `Integragal` ou `IntegragalGit`
- ‚úÖ Corrige todos os caminhos hardcoded para funcionar localmente
- ‚úÖ Atualiza `config.json` com caminhos relativos
- ‚úÖ Corrige `auth_service.py` para usar caminhos locais
- ‚úÖ Ajusta `user_management.py` e `admin_panel.py`
- ‚úÖ Cria backup de todos os arquivos modificados
- ‚úÖ Gera `executar.bat` adaptado √† estrutura

## üöÄ Execu√ß√£o Ap√≥s Corre√ß√£o

### M√©todo 1: Via Command Prompt
```bash
cd C:\Users\marci\Downloads\Integragal
python main.py
```

### M√©todo 2: Via Batch (executar.bat)
```bash
# Clicar duas vezes em:
executar.bat
```

## üìã Arquivos Importantes

### Arquivos que SER√ÉO modificados:
- `config.json` - Caminhos relativos
- `autenticacao/auth_service.py` - Imports e paths
- `ui/user_management.py` - Caminhos de arquivos
- `ui/admin_panel.py` - Refer√™ncias de arquivo

### Arquivos que SER√ÉO criados:
- `executar.bat` - Script de execu√ß√£o adaptado
- M√∫ltiplos backups: `*.backup_YYYYMMDD_HHMMSS`

## ÔøΩ‚Äù¬ç Verifica√ß√£o P√≥s-Corre√ß√£o

### Check-list:
- [ ] Script executou sem erros
- [ ] Todos os arquivos foram encontrados
- [ ] `executar.bat` foi criado
- [ ] Backup dos arquivos originais feito

### Teste de Funcionamento:
1. **Login**: `marcio` / `flafla`
2. **Painel Admin**: Testar edi√ß√£o da Base URL GAL
3. **Gerenciamento Usu√°rios**: Verificar se n√£o h√° erro de campo senha
4. **Fechamento**: Confirmar que janelas fecham com um clique

## ÔøΩ‚Ä∫¬†√Ø¬∏¬è Corre√ß√£o Manual (se necess√°rio)

### 1. Verificar config.json
```json
{
    "paths": {
        "log_file": "logs/sistema.log",
        "exams_catalog_csv": "banco/exames_config.csv", 
        "credentials_csv": "banco/usuarios.csv",
        "gal_history_csv": "logs/total_importados_gal.csv"
    }
}
```

### 2. Verificar auth_service.py
Linha 53 deve estar:
```python
CAMINHO_CREDENCIAIS = "banco/usuarios.csv"  # Caminho relativo
```

### 3. Verificar user_management.py
Linha 31 deve estar:
```python
self.usuarios_path = os.path.join("banco", "usuarios.csv")
```

## √¢¬ù‚Äî Problemas Comuns

### "main.py n√£o encontrado"
**Solu√ß√£o**: Navegar para pasta correta
```bash
cd C:\Users\marci\Downloads\Integragal
```

### "ModuleNotFoundError"
**Solu√ß√£o**: Instalar depend√™ncias
```bash
pip install customtkinter pandas bcrypt
```

### "Arquivo n√£o encontrado"
**Solu√ß√£o**: Verificar estrutura de pastas
```
Integragal/
√¢‚Äù≈ì√¢‚Äù‚Ç¨√¢‚Äù‚Ç¨ main.py
√¢‚Äù≈ì√¢‚Äù‚Ç¨√¢‚Äù‚Ç¨ config.json
√¢‚Äù≈ì√¢‚Äù‚Ç¨√¢‚Äù‚Ç¨ autenticacao/
√¢‚Äù≈ì√¢‚Äù‚Ç¨√¢‚Äù‚Ç¨ ui/
√¢‚Äù≈ì√¢‚Äù‚Ç¨√¢‚Äù‚Ç¨ banco/
√¢‚Äù‚Äù√¢‚Äù‚Ç¨√¢‚Äù‚Ç¨ logs/
```

## ÔøΩ‚Äú≈æ Suporte

Se ainda houver problemas:
1. Executar script de corre√ß√£o novamente
2. Verificar se todos os arquivos do package foram extra√≠dos
3. Confirmar que est√° na pasta `C:\Users\marci\Downloads\Integragal`
4. Testar comando: `python main.py`

---
**Data**: 02/12/2025  
**Status**: ‚úÖ Corre√ß√µes autom√°ticas implementadas