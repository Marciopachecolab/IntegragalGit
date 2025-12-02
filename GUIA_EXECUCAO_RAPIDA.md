# 🚀 GUIA DE EXECUÇÃO RÁPIDA - IntegraGAL

## 📦 Após Extrair o Pacote:

### Opção 1: Usar o executar.bat (RECOMENDADO)
1. **Extrair** o arquivo `IntegraGAL_CorrecaoSegura_20251202_113410.zip`
2. **Clicar duas vezes** no arquivo `executar.bat`
3. **Aguardar** o sistema abrir

### Opção 2: Execução Manual
Se o .bat não funcionar:
1. **Abrir** Prompt de Comando (cmd) na pasta extraída
2. **Digitar:** `python main.py`
3. **Pressionar Enter**

### Opção 3: Usar executar_simples.bat
Se o executar.bat der problemas:
- Usar o arquivo `executar_simples.bat`

## 🔍 Testando as Correções:

### 1. **Base URL GAL**
- ✅ Abrir → Admin Panel → Sistema
- ✅ Alterar a URL do GAL
- ✅ Clicar "Salvar"
- ✅ **Esperado:** Mensagem de sucesso
- ✅ **Fechar e reabrir** o painel
- ✅ **Verificar:** A nova URL deve estar mantida

### 2. **Gerenciamento de Usuários**
- ✅ Abrir → Ferramentas → Gerenciar Usuários
- ✅ **Esperado:** Deve abrir **SEM erro "senha_hash"**
- ✅ A janela deve abrir normalmente

### 3. **Fechamento da Janela**
- ✅ Abrir o Gerenciamento de Usuários
- ✅ **Clicar no X** para fechar
- ✅ **Esperado:** Fecha com **1 clique** (não precisa clicar várias vezes)

## 📋 Login Padrão:
- **Usuário:** `marcio`
- **Senha:** `flafla`

## ⚠️ Problemas Conhecidos Resolvidos:
1. ❌ ~~Base URL GAL voltava ao valor original~~ → ✅ **CORRIGIDO**
2. ❌ ~~Erro "senha_hash" no gerenciamento~~ → ✅ **CORRIGIDO**  
3. ❌ ~~Janela não fechava com 1 clique~~ → ✅ **CORRIGIDO**
4. ❌ ~~Múltiplas janelas abertas~~ → ✅ **CORRIGIDO**

## 📞 Se ainda tiver problemas:
1. Verificar se o Python está instalado
2. Verificar se as dependências estão instaladas: `pip install customtkinter bcrypt`
3. Verificar se os arquivos foram extraídos corretamente com estrutura de pastas

---
**✅ Pacote:** `IntegraGAL_CorrecaoSegura_20251202_113410.zip`
**📅 Data:** 02/12/2025 11:34
**🔧 Status:** Correções Seguras e Conservadoras Aplicadas