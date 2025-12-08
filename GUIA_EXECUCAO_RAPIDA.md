# ğŸš€ GUIA DE EXECUÃ‡ÃƒO RÃ�PIDA - IntegraGAL





## ï¿½“Â¦ Após Extrair o Pacote:





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





## ï¿½â€�Â� Testando as Correções:





### 1. **Base URL GAL**


- âœ… Abrir ââ€ ’ Admin Panel ââ€ ’ Sistema


- âœ… Alterar a URL do GAL


- âœ… Clicar "Salvar"


- âœ… **Esperado:** Mensagem de sucesso


- âœ… **Fechar e reabrir** o painel


- âœ… **Verificar:** A nova URL deve estar mantida





### 2. **Gerenciamento de Usuários**


- âœ… Abrir ââ€ ’ Ferramentas ââ€ ’ Gerenciar Usuários


- âœ… **Esperado:** Deve abrir **SEM erro "senha_hash"**


- âœ… A janela deve abrir normalmente





### 3. **Fechamento da Janela**


- âœ… Abrir o Gerenciamento de Usuários


- âœ… **Clicar no X** para fechar


- âœ… **Esperado:** Fecha com **1 clique** (não precisa clicar várias vezes)





## ğŸ“‹ Login Padrão:


- **Usuário:** `marcio`


- **Senha:** `flafla`





## âÅ¡Â ïÂ¸Â� Problemas Conhecidos Resolvidos:


1. âÂ�Å’ ~~Base URL GAL voltava ao valor original~~ ââ€ ’ âœ… **CORRIGIDO**


2. âÂ�Å’ ~~Erro "senha_hash" no gerenciamento~~ ââ€ ’ âœ… **CORRIGIDO**  


3. âÂ�Å’ ~~Janela não fechava com 1 clique~~ ââ€ ’ âœ… **CORRIGIDO**


4. âÂ�Å’ ~~Múltiplas janelas abertas~~ ââ€ ’ âœ… **CORRIGIDO**





## ï¿½“Å¾ Se ainda tiver problemas:


1. Verificar se o Python está instalado


2. Verificar se as dependências estão instaladas: `pip install customtkinter bcrypt`


3. Verificar se os arquivos foram extraídos corretamente com estrutura de pastas





---


**âœ… Pacote:** `IntegraGAL_CorrecaoSegura_20251202_113410.zip`


**ï¿½“… Data:** 02/12/2025 11:34


**ğŸ›  Status:** Correções Seguras e Conservadoras Aplicadas