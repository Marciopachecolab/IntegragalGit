# Guia de Execu√ßão para C:\Users\marci\Downloads\Integragal





## üéØ Problema Identificado


O sistema IntegraGAL está sendo executado em `C:\Users\marci\Downloads\Integragal` (não em `IntegragalGit`), então os caminhos precisam ser corrigidos.





## ‚úÖ Solu√ßão: Script de Corre√ßão Automática





### 1. Executar o Script de Corre√ßão


```bash


# Navegar para a pasta do sistema


cd C:\Users\marci\Downloads\Integragal





# Executar o script de corre√ßão


python corrigir_caminhos_integragal.py


```





### 2. O que o script faz:


- ‚úÖ Detecta automaticamente se é estrutura `Integragal` ou `IntegragalGit`


- ‚úÖ Corrige todos os caminhos hardcoded para funcionar localmente


- ‚úÖ Atualiza `config.json` com caminhos relativos


- ‚úÖ Corrige `auth_service.py` para usar caminhos locais


- ‚úÖ Ajusta `user_management.py` e `admin_panel.py`


- ‚úÖ Cria backup de todos os arquivos modificados


- ‚úÖ Gera `executar.bat` adaptado √† estrutura





## üöÄ Execu√ßão Ap√≥s Corre√ßão





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





## üìã Arquivos Importantes





### Arquivos que SERÉO modificados:


- `config.json` - Caminhos relativos


- `autenticacao/auth_service.py` - Imports e paths


- `ui/user_management.py` - Caminhos de arquivos


- `ui/admin_panel.py` - Refer√™ncias de arquivo





### Arquivos que SERÉO criados:


- `executar.bat` - Script de execu√ßão adaptado


- M√∫ltiplos backups: `*.backup_YYYYMMDD_HHMMSS`





## ÔøΩ‚Äù¬ç Verifica√ßão P√≥s-Corre√ßão





### Check-list:


- [ ] Script executou sem erros


- [ ] Todos os arquivos foram encontrados


- [ ] `executar.bat` foi criado


- [ ] Backup dos arquivos originais feito





### Teste de Funcionamento:


1. **Login**: `marcio` / `flafla`


2. **Painel Admin**: Testar edi√ßão da Base URL GAL


3. **Gerenciamento Usuários**: Verificar se não há erro de campo senha


4. **Fechamento**: Confirmar que janelas fecham com um clique





## ÔøΩ‚Ä∫¬†√Ø¬∏¬è Corre√ßão Manual (se necessário)





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





## â¬ù‚Äî Problemas Comuns





### "main.py não encontrado"


**Solu√ßão**: Navegar para pasta correta


```bash


cd C:\Users\marci\Downloads\Integragal


```





### "ModuleNotFoundError"


**Solu√ßão**: Instalar depend√™ncias


```bash


pip install customtkinter pandas bcrypt


```





### "Arquivo não encontrado"


**Solu√ßão**: Verificar estrutura de pastas


```


Integragal/


â‚Äù≈ìâ‚Äù‚Ç¨â‚Äù‚Ç¨ main.py


â‚Äù≈ìâ‚Äù‚Ç¨â‚Äù‚Ç¨ config.json


â‚Äù≈ìâ‚Äù‚Ç¨â‚Äù‚Ç¨ autenticacao/


â‚Äù≈ìâ‚Äù‚Ç¨â‚Äù‚Ç¨ ui/


â‚Äù≈ìâ‚Äù‚Ç¨â‚Äù‚Ç¨ banco/


â‚Äù‚Äùâ‚Äù‚Ç¨â‚Äù‚Ç¨ logs/


```





## ÔøΩ‚Äú≈æ Suporte





Se ainda houver problemas:


1. Executar script de corre√ßão novamente


2. Verificar se todos os arquivos do package foram extra√≠dos


3. Confirmar que está na pasta `C:\Users\marci\Downloads\Integragal`


4. Testar comando: `python main.py`





---


**Data**: 02/12/2025  


**Status**: ‚úÖ Corre√ß√µes automáticas implementadas