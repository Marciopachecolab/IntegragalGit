# IntegraGAL

IntegraGAL é um sistema de apoio à **análise de dados de Biologia Molecular** e **integração com o sistema GAL** (Sistema Gerenciador de Ambiente Laboratorial), com foco em laboratórios de saúde pública.

Ele foi desenhado para organizar o fluxo de:

1. **Configuração de exames, métodos e painéis**
2. **Importação e processamento de resultados de qPCR/RT-PCR**
3. **Visualização e validação de placas**
4. **Geração de arquivos e envio de resultados ao GAL**
5. **Registro de logs, rastreabilidade e apoio à auditoria**

---

## 📁 Estrutura geral do projeto

Principais diretórios e arquivos:

- `analise/`  
  Módulos de análise e processamento de placas (ex.: scripts específicos para plataformas/formatos, como Biomanguinhos 7500).

- `autenticacao/`  
  Fluxo de login, autenticação e carregamento de credenciais.

- `exportacao/`  
  Rotinas de **envio de resultados para o GAL**, leitura de CSV e integração com serviços externos.

- `ui/`  
  Interface gráfica (CustomTkinter), incluindo:
  - `main_window.py`: janela principal (“IntegraGAL – Menu Principal”)
  - `menu_handler.py`: organização dos menus e ações
  - `admin_panel.py`: painel administrativo e de configuração

- `utils/`  
  Funções utilitárias (logs, operações de GUI, helpers diversos).

- `tests/`  
  Scripts de teste e mock (ex.: geração de planilhas de controle, casos de “não detectado” etc.).

- `config.json` / `configuracao/`  
  Arquivos de configuração (paths, integrações, parâmetros de análise).

- Documentação específica:
  - `GUIA_EXECUCAO_INTEGRAGAL.md`
  - `GUIA_EXECUCAO_RAPIDA.md`
  - `INSTRUCOES_DEPLOY.md`
  - `INSTRUCOES_INTEGRAGAL.md`

---

## 📦 Requisitos

- **Python 3.x** (recomenda-se a mesma versão utilizada em produção / no laboratório)
- Ambiente Windows (desenvolvido e testado originalmente em Windows)
- Bibliotecas principais (parcial):
  - `pandas`
  - `customtkinter`
  - `simplejson`
  - `selenium` (para integrações automatizadas quando necessário)
  - `openpyxl`
  - Outras dependências listadas em `requirements.txt` (se disponível)

> Ajuste este bloco conforme a sua instalação oficial (versão do Python e arquivo de requisitos).

---

## 🚀 Instalação

1. **Clonar o repositório**

   ```bash
   git clone https://github.com/SEU_USUARIO/SEU_REPO_INTEGRAGAL.git
   cd SEU_REPO_INTEGRAGAL
