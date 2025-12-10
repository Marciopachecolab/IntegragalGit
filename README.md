# 🧬 IntegRAGal

**Sistema Integrado para Análise de PCR em Tempo Real e Integração com GAL**

[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)](CHANGELOG.md)
[![Tests](https://img.shields.io/badge/tests-113%20passed-brightgreen.svg)](tests/)

---

## 📋 Sobre o Projeto

**IntegRAGal** é uma aplicação desktop desenvolvida em Python para laboratórios de biologia molecular, especializada em:

- 🔬 **Análise Automatizada** de resultados de qPCR/RT-PCR (QuantStudio 3/5/7)
- ✅ **Validação Inteligente** com regras de controle de qualidade
- 🔔 **Sistema de Alertas** em tempo real para problemas detectados
- 📊 **Geração de Relatórios** profissionais (PDF, Excel, CSV)
- 🌐 **Integração com GAL** (Gerenciador de Ambiente Laboratorial - Ministério da Saúde)
- 🎨 **Interface Moderna** com CustomTkinter (modo claro/escuro)

### Principais Funcionalidades

✨ **Detecção Automática de Equipamentos**: Reconhece automaticamente arquivos do QuantStudio  
✨ **Validação de Controles**: Verifica controles positivos/negativos automaticamente  
✨ **Detecção de Outliers**: Identifica valores estatisticamente anormais  
✨ **Mapeamento de Placas**: Associa placas a protocolos e amostras  
✨ **Histórico Completo**: Mantém registro de todas as análises realizadas  
✨ **Configuração Flexível**: 11 categorias de configurações personalizáveis  
✨ **Backup Automático**: Sistema de backup e recuperação de configurações  

---

## 🚀 Início Rápido

### Instalação Express (5 minutos)

```powershell
# 1. Descompacte o arquivo
# 2. Abra PowerShell na pasta do sistema
cd C:\IntegRAGal

# 3. Execute o instalador
.\install.bat

# 4. Aguarde instalação das dependências (~2-3 minutos)

# 5. Inicie o sistema
python main.py
```

### Primeira Análise (5 minutos)

1. **Login**: `admin` / `admin123`
2. **Importar**: Extração → Selecionar arquivo Excel do QuantStudio
3. **Validar**: Sistema detecta equipamento e valida dados automaticamente
4. **Analisar**: Revise resultados e alertas gerados
5. **Exportar**: Gere relatório em PDF/Excel/CSV

📖 **Guia Completo**: [`docs/GUIA_INICIO_RAPIDO.md`](docs/GUIA_INICIO_RAPIDO.md)

---

## 📚 Documentação

| Documento | Descrição | Público |
|-----------|-----------|---------|
| [**Manual do Usuário**](docs/MANUAL_USUARIO.md) | Guia completo com todas as funcionalidades | Usuários finais |
| [**Guia de Início Rápido**](docs/GUIA_INICIO_RAPIDO.md) | Onboarding de 10 minutos | Novos usuários |
| [**FAQ**](docs/FAQ.md) | 60 perguntas frequentes | Todos |
| [**Troubleshooting**](docs/TROUBLESHOOTING.md) | Resolução de problemas | Usuários/Admins |
| [**Arquitetura Técnica**](docs/ARQUITETURA_TECNICA.md) | Documentação para desenvolvedores | Desenvolvedores |

### Guias de Execução

- [`GUIA_EXECUCAO_INTEGRAGAL.md`](GUIA_EXECUCAO_INTEGRAGAL.md): Guia detalhado de execução
- [`INSTRUCOES_DEPLOY.md`](INSTRUCOES_DEPLOY.md): Instruções de deployment
- [`TODO.md`](TODO.md): Roadmap e tarefas planejadas

---

## 🏗️ Arquitetura

### Stack Tecnológico

```
Python 3.13  |  CustomTkinter 5.2  |  Pandas 2.1  |  Matplotlib 3.8
ReportLab 4.0  |  OpenPyXL 3.1  |  Requests 2.31  |  Pytest 7.4
```

### Estrutura do Projeto

```
IntegRAGal/
├── main.py                  # Ponto de entrada
├── models.py                # Modelos de dados
├── config.json              # Configurações do sistema
│
├── interface/               # Interface gráfica (CustomTkinter)
│   ├── dashboard.py         # Tela principal
│   ├── tela_extracao.py     # Módulo de importação
│   ├── tela_analise.py      # Visualização de resultados
│   └── tela_configuracoes.py # Gerenciamento de configurações
│
├── extracao/                # Detecção e parsing de equipamentos
│   ├── busca_extracao.py    # Detecção automática
│   └── mapeamento_placas.py # Mapeamento de placas
│
├── analise/                 # Regras de validação e análise
│   ├── relatorios_qualidade_gerenciais.py  # Motor de regras
│   └── relatorios_operacionais.py          # Análises operacionais
│
├── exportacao/              # Geração de relatórios
│   ├── exportar_resultados.py  # PDF/Excel/CSV
│   └── envio_gal.py            # Integração com GAL
│
├── config/                  # Sistema de configuração (Fase 4.4)
│   ├── settings.py          # ConfigurationManager (Singleton)
│   └── default_config.json  # Configurações padrão
│
├── utils/                   # Utilitários e infraestrutura
│   ├── persistence.py       # Gerenciamento de estado e cache
│   ├── error_handler.py     # Tratamento centralizado de erros
│   └── validator.py         # Validações de dados
│
├── banco/                   # Banco de dados CSV
│   ├── usuarios.csv         # Credenciais (hasheadas)
│   ├── equipamentos.csv     # Equipamentos cadastrados
│   ├── placas.csv           # Mapeamento de placas
│   └── regras.csv           # Regras customizadas
│
├── tests/                   # Suite de testes (113 testes)
│   ├── test_integracao_completa.py  # 9 testes de integração
│   ├── test_performance.py          # 5 benchmarks
│   ├── test_memory.py               # Testes de stress
│   └── test_configuracoes_persistencia.py  # 15 testes
│
└── docs/                    # Documentação completa
    ├── MANUAL_USUARIO.md
    ├── GUIA_INICIO_RAPIDO.md
    ├── FAQ.md
    ├── TROUBLESHOOTING.md
    └── ARQUITETURA_TECNICA.md
```

### Design Patterns

- **Singleton**: ConfigurationManager, AlertManager
- **Observer**: Sistema de alertas e notificações
- **Strategy**: Detecção de equipamentos, exportação de relatórios
- **Decorator**: Error handling, logging
- **Factory**: Criação de alertas e validators

📖 **Detalhes**: [`docs/ARQUITETURA_TECNICA.md`](docs/ARQUITETURA_TECNICA.md)



---

## 🔧 Requisitos do Sistema

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| **Sistema Operacional** | Windows 10 | Windows 11 |
| **Python** | 3.10 | 3.13 |
| **RAM** | 4 GB | 8 GB |
| **Processador** | Dual-core | Quad-core |
| **Espaço em Disco** | 500 MB | 2 GB (com dados) |
| **Resolução** | 1280x720 | 1920x1080 |

---

## 📦 Instalação e Dependências

### Instalação Automática (Recomendado)

```powershell
# 1. Clone o repositório ou baixe o ZIP
git clone https://github.com/Marciopachecolab/IntegRAGal.git
cd IntegRAGal

# 2. Execute o instalador automático
.\install.bat

# 3. Aguarde instalação (~2-3 minutos)
# O script irá:
# - Criar ambiente virtual (venv)
# - Instalar todas as dependências
# - Verificar integridade do sistema

# 4. Inicie o sistema
python main.py
```

### Instalação Manual

Se preferir ou se `install.bat` falhar:

```powershell
# 1. Crie ambiente virtual
python -m venv venv

# 2. Ative o ambiente
.\venv\Scripts\Activate.ps1

# 3. Atualize pip
python -m pip install --upgrade pip

# 4. Instale dependências
pip install -r requirements.txt

# 5. Verifique instalação
python -c "import customtkinter; print('✓ Instalação OK')"

# 6. Inicie o sistema
python main.py
```

### Dependências Principais

```txt
# Interface
customtkinter==5.2.2
Pillow==10.1.0

# Análise de Dados
pandas==2.1.4
numpy==1.26.2

# Visualização
matplotlib==3.8.2

# Exportação
reportlab==4.0.7
openpyxl==3.1.2

# HTTP Client (integração GAL)
requests==2.31.0

# Testes
pytest==7.4.3
pytest-cov==4.1.0
```

📄 **Lista Completa**: [`requirements.txt`](requirements.txt)

---

## 🧪 Testes

### Executar Suite Completa

```powershell
# Todos os testes (113 testes)
pytest tests/ -v

# Com cobertura
pytest tests/ --cov --cov-report=html

# Testes específicos
pytest tests/test_integracao_completa.py -v
pytest tests/test_performance.py -v
```

### Resultados Atuais (v1.0.0)

```
✅ Fase 1: Equipment Detection - 42 testes (100%)
✅ Fase 2: Parser + Rules Engine - 95 testes (100%, 69% coverage)
✅ Fase 4.1: Integration Tests - 9 testes (100%)
✅ Fase 4.2: Performance Benchmarks - 5 testes (100%)
✅ Fase 4.3: Memory Stress Tests - 8 testes (100%)
✅ Fase 4.4: Configuration & Persistence - 15 testes (100%)

TOTAL: 113 testes | 100% pass rate | Coverage: 69%
```

### Benchmarks de Performance

| Operação | Tempo | Limite | Status |
|----------|-------|--------|--------|
| Carregar dashboard | 459 ms | < 500 ms | ✅ |
| Criar alerta | 0.08 ms | < 1 ms | ✅ |
| Filtrar 1000 amostras | 0.04 ms | < 10 ms | ✅ |
| Exportar PDF (100 amostras) | 2.3 s | < 5 s | ✅ |
| Enviar GAL (50 amostras) | 4.1 s | < 10 s | ✅ |

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja como contribuir:

### Setup de Desenvolvimento

```powershell
# 1. Fork e clone o repositório
git clone https://github.com/seu-usuario/IntegRAGal.git
cd IntegRAGal

# 2. Crie branch para feature
git checkout -b feature/minha-feature

# 3. Instale dependências de desenvolvimento
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Execute testes
pytest tests/ -v

# 5. Lint e formatação
flake8 --max-line-length=100 *.py */**.py
black .

# 6. Commit e push
git add .
git commit -m "feat: adiciona minha feature"
git push origin feature/minha-feature

# 7. Abra Pull Request no GitHub
```

### Convenções de Código

- Seguir **PEP 8**
- **Type hints** obrigatórios em funções públicas
- **Docstrings** no formato Google Style
- **Commits** seguir Conventional Commits (`feat:`, `fix:`, `docs:`)
- **Testes** para novas funcionalidades

### Reportar Bugs

Encontrou um problema? [Abra uma issue](https://github.com/Marciopachecolab/IntegRAGal/issues) com:

- Descrição clara do problema
- Passos para reproduzir
- Mensagem de erro completa
- Logs do sistema (se aplicável)
- Versão do sistema (`python main.py --version`)

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License**. Veja o arquivo [`LICENSE`](LICENSE) para detalhes.

---

## 👥 Autores e Contato

**Desenvolvedor Principal**: Márcio Pacheco  
**Instituição**: Laboratório Central de Saúde Pública (LACEN)  
**Email**: marcio@integragal.com  
**GitHub**: [@Marciopachecolab](https://github.com/Marciopachecolab)

### Suporte

- **GitHub Issues**: https://github.com/Marciopachecolab/IntegRAGal/issues
- **Email**: suporte@integragal.com
- **Documentação**: [`docs/`](docs/)

---

## 📊 Status do Projeto

### Versão Atual: **v1.0.0** (Dezembro 2025)

**Fases Completas**:
- ✅ Fase 1: Equipment Detection (42 testes, 100%)
- ✅ Fase 2: Parser + Rules Engine (95 testes, 69% coverage)
- ✅ Fase 3: Interface Gráfica (6 etapas, 4034 linhas)
- ✅ Fase 4: Testes e Integração Final (6 etapas, 100%)

**Total**: ~8.000 linhas de código | 113 testes | 100% Fase 4

### Roadmap

#### v1.1 (Q1 2026)
- [ ] API REST para integração externa
- [ ] Processamento em lote (múltiplas placas)
- [ ] Suporte a PostgreSQL
- [ ] Dashboard Web (Flask/FastAPI)

#### v1.2 (Q2 2026)
- [ ] Multilíngue (Inglês, Espanhol)
- [ ] Permissões granulares (RBAC)
- [ ] Integração com LIMS
- [ ] Relatórios customizáveis (drag-and-drop)

#### v1.3 (Q3 2026)
- [ ] Machine Learning (predição de falhas)
- [ ] App Mobile (visualização/aprovação)
- [ ] Cloud Storage (Azure/AWS)
- [ ] Colaboração em equipe (comentários, aprovações)

📋 **Detalhes**: [`TODO.md`](TODO.md)

---

## 🙏 Agradecimentos

- **Ministério da Saúde** pelo sistema GAL
- **Applied Biosystems** pelos equipamentos QuantStudio
- **Comunidade Python** pelas excelentes bibliotecas
- **Todos os colaboradores** que tornaram este projeto possível

---

## 📈 Estatísticas

![GitHub stars](https://img.shields.io/github/stars/Marciopachecolab/IntegRAGal?style=social)
![GitHub forks](https://img.shields.io/github/forks/Marciopachecolab/IntegRAGal?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/Marciopachecolab/IntegRAGal?style=social)

---

**Feito com ❤️ para a comunidade de laboratórios de saúde pública brasileiros**



   ```bash

python -m venv venv

# Componentes oficiais (implementação atual)

- services/universal_engine.py + services/analysis_service.py: pipeline de análise universal.
- services/history_report.py: histórico oficial (reports/historico_analises.csv).
- services/plate_viewer.py: visualizador oficial de placa usando df_final em memória.
- fix_encoding_safe.py: utilitário recomendado para correções de encoding/mojibake.
