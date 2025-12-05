# IntegraGAL – Sistema de Análise e Integração de Dados de Biologia Molecular com o GAL

O **IntegraGAL** é uma aplicação desktop desenvolvida em Python para apoiar laboratórios de biologia molecular na **análise de corridas de qPCR/RT-PCR**, consolidação de resultados e **integração com o sistema GAL** (Gerenciador de Ambiente Laboratorial).  
O sistema organiza o fluxo desde os arquivos de extração e resultados até a geração de saídas padronizadas e prontas para envio ao GAL.

---

## 1. Arquitetura em alto nível

A arquitetura do IntegraGAL está organizada em camadas, com separação clara entre interface gráfica, regras de negócio e infraestrutura:

1. **Interface de Usuário (UI) – Tkinter/CustomTkinter**
   - Janela principal da aplicação.
   - Menus para:
     - Seleção de arquivos (CSV de extração, CSV de resultados).
     - Execução dos motores de análise (protocolos/placas).
     - Visualização de mapas de trabalho e resultados consolidados.
     - Módulo de *Cadastros Diversos* (exames, equipamentos, placas, regras).
     - Configurações gerais do sistema.
   - Componentes de feedback visual (barras de progresso, mensagens de status, etc.).

2. **Camada de Serviços**
   - **Serviços de análise**: orquestram a chamada dos motores específicos (por equipamento/kit) e do motor universal.
   - **Serviço de configuração (`config_service`)**:
     - Carregamento e persistência das configurações da aplicação.
   - **Serviço de integração GAL**:
     - Formatação dos resultados no padrão aceito pelo GAL.
     - Preparação de arquivos/objetos para envio (via upload manual ou rotinas de automação).
   - **Serviços auxiliares**:
     - Validação de dados de entrada (estrutura dos CSVs, tipos de dados).
     - Geração de arquivos de saída (CSV consolidado, relatórios, etc.).

3. **Motores de Análise**
   - **Motores específicos** (por kit/protocolo/equipamento):
     - Ex.: `vr1e2_biomanguinhos_7500.py`, outros scripts dedicados.
   - **Motor universal de análise**:
     - Padroniza o processamento para diferentes placas/equipamentos.
     - Produz um `df_final` com o mesmo formato dos motores específicos consolidados.
   - Regras de interpretação (positivo/negativo/inconclusivo, cortes de Ct, etc.) configuráveis a partir das regras cadastradas.

4. **Infraestrutura e Núcleo Comum**
   - **`AppState`**:
     - Estrutura única que guarda o estado global da aplicação (configuração, caminhos, usuário corrente, contexto da corrida, etc.).
   - **`system_paths`**:
     - Responsável por definir e centralizar os diretórios de trabalho (config, dados, logs, exportações, temporários).
   - **`logger`**:
     - Sistema de registro de logs da aplicação, com saída em arquivo e console.
   - **Camada de persistência (quando aplicável)**:
     - Banco de dados local ou arquivos para armazenamento de histórico, log de operações e outras informações.

---

## 2. Dependências e instalação

### 2.1 Pré-requisitos

- **Sistema operacional**: Windows (ambiente de desenvolvimento principal).
- **Python**: versão 3.13 (ou a versão definida no projeto).
- **Git** (opcional, se o código for obtido via repositório Git).

Os demais pacotes Python devem estar listados em `requirements.txt`.

### 2.2 Passos de instalação

1. **Obter o código-fonte**

   - Via Git:
     ```bash
     git clone <URL_DO_REPOSITORIO>
     cd Integragal
     ```

   - Ou extraindo o `.zip` do projeto para uma pasta, por exemplo:
     `C:\Users\marci\Downloads\Integragal`

2. **Criar um ambiente virtual**

   ```bash
   python -m venv venv
