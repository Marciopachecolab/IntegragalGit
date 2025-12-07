# 📋 INSTRUÇÕES DE INSTALAÇÃO E EXECUÇÃO

## 🎯 Para executar em: C:\Users\marci\Downloads\Integragal

### PASSO 1: Extrair o Package
1. Baixar o arquivo: `IntegraGAL_Integragal_Completo_YYYYMMDD_HHMMSS.zip`
2. Extrair em: `C:\Users\marci\Downloads\Integragal`
3. Verificar se os arquivos ficaram na pasta `Integragal`

### PASSO 2: Executar Correção Automática
```bash
cd C:\Users\marci\Downloads\Integragal
python corrigir_caminhos_integragal.py
```

### PASSO 3: Iniciar o Sistema
```bash
python main.py
```
OU
```bash
executar.bat
```

## �Ž® Login do Sistema
- **Usuário**: `marcio`
- **Senha**: `flafla`

## ✅ Testes das Correções Implementadas

### 1. Base URL GAL
- Ir para: Painel Administrativo â†’ Sistema
- Verificar se "Base URL GAL" é editável (campo editável)
- Alterar valor e clicar "Salvar Alterações"
- Sair e entrar novamente para verificar se salvou

### 2. Gerenciamento de Usuários
- Ir para: Ferramentas â†’ Gerenciar Usuários
- Verificar se NÃO aparece erro "X Erro ao carregar usuário: 'senha'"
- Lista deve mostrar 4 usuários

### 3. Fechamento de Janelas
- Abrir qualquer módulo (Admin ou Usuários)
- Clicar no X de fechar
- Verificar se fecha com um clique (não múltiplos)

## �› ï¸ Arquivos Importantes

### Arquivos Principais (raiz):
- `main.py` - Arquivo principal do sistema
- `config.json` - Configurações do sistema
- `executar.bat` - Script de execução
- `corrigir_caminhos_integragal.py` - Script de correção

### Pastas Importantes:
- `banco/` - Arquivos CSV (usuarios.csv, configuracoes, etc.)
- `autenticacao/` - Sistema de login
- `ui/` - Interface gráfica
- `logs/` - Logs do sistema (será criada automaticamente)

## â— Solução de Problemas

### "main.py não encontrado"
â†’ Verificar se extraiu corretamente em `C:\Users\marci\Downloads\Integragal`

### "ModuleNotFoundError"
â†’ Instalar dependências:
```bash
pip install customtkinter pandas bcrypt
```

### "Arquivo não encontrado"
â†’ Executar o script de correção:
```bash
python corrigir_caminhos_integragal.py
```

### Janela não abre
â†’ Verificar se tem Python instalado:
```bash
python --version
```

## �“ž Contato
Em caso de problemas, verificar arquivo `LEIA_PRIMEIRO.md` para mais detalhes.

---
**Data**: 02/12/2025  
**Sistema**: IntegraGAL v2.0 - Correções para Integragal  
**Status**: ✅ Pronto para execução
