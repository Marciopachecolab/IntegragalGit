# Guia de Execução para C:\Users\marci\Downloads\Integragal

## 🎯 Problema Identificado
O sistema IntegraGAL está sendo executado em `C:\Users\marci\Downloads\Integragal` (não em `IntegragalGit`), então os caminhos precisam ser corrigidos.

## ✅ Solução: Script de Correção Automática

### 1. Executar o Script de Correção
```bash
# Navegar para a pasta do sistema
cd C:\Users\marci\Downloads\Integragal

# Executar o script de correção
python corrigir_caminhos_integragal.py
```

### 2. O que o script faz:
- ✅ Detecta automaticamente se é estrutura `Integragal` ou `IntegragalGit`
- ✅ Corrige todos os caminhos hardcoded para funcionar localmente
- ✅ Atualiza `config.json` com caminhos relativos
- ✅ Corrige `auth_service.py` para usar caminhos locais
- ✅ Ajusta `user_management.py` e `admin_panel.py`
- ✅ Cria backup de todos os arquivos modificados
- ✅ Gera `executar.bat` adaptado à estrutura

## 🚀 Execução Após Correção

### Método 1: Via Command Prompt
```bash
cd C:\Users\marci\Downloads\Integragal
python main.py
```

### Método 2: Via Batch (executar.bat)
```bash
# Clicar duas vezes em:
executar.bat
```

## 📋 Arquivos Importantes

### Arquivos que SERÃO modificados:
- `config.json` - Caminhos relativos
- `autenticacao/auth_service.py` - Imports e paths
- `ui/user_management.py` - Caminhos de arquivos
- `ui/admin_panel.py` - Referências de arquivo

### Arquivos que SERÃO criados:
- `executar.bat` - Script de execução adaptado
- Múltiplos backups: `*.backup_YYYYMMDD_HHMMSS`

## �” Verificação Pós-Correção

### Check-list:
- [ ] Script executou sem erros
- [ ] Todos os arquivos foram encontrados
- [ ] `executar.bat` foi criado
- [ ] Backup dos arquivos originais feito

### Teste de Funcionamento:
1. **Login**: `marcio` / `flafla`
2. **Painel Admin**: Testar edição da Base URL GAL
3. **Gerenciamento Usuários**: Verificar se não há erro de campo senha
4. **Fechamento**: Confirmar que janelas fecham com um clique

## �› ï¸ Correção Manual (se necessário)

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

## â— Problemas Comuns

### "main.py não encontrado"
**Solução**: Navegar para pasta correta
```bash
cd C:\Users\marci\Downloads\Integragal
```

### "ModuleNotFoundError"
**Solução**: Instalar dependências
```bash
pip install customtkinter pandas bcrypt
```

### "Arquivo não encontrado"
**Solução**: Verificar estrutura de pastas
```
Integragal/
â”œâ”€â”€ main.py
â”œâ”€â”€ config.json
â”œâ”€â”€ autenticacao/
â”œâ”€â”€ ui/
â”œâ”€â”€ banco/
â””â”€â”€ logs/
```

## �“ž Suporte

Se ainda houver problemas:
1. Executar script de correção novamente
2. Verificar se todos os arquivos do package foram extraídos
3. Confirmar que está na pasta `C:\Users\marci\Downloads\Integragal`
4. Testar comando: `python main.py`

---
**Data**: 02/12/2025  
**Status**: ✅ Correções automáticas implementadas