# 📚 Índice de Documentação - IntegRAGal

**Última Atualização**: 10 de dezembro de 2025  
**Versão do Sistema**: 1.0.0

---

## 🚀 Início Rápido

Novos usuários devem começar por aqui:

1. **[README.md](README.md)** - Visão geral completa do sistema
2. **[LEITURA_5MIN.md](LEITURA_5MIN.md)** - Introdução rápida (5 minutos)
3. **[GUIA_EXECUCAO_RAPIDA.md](GUIA_EXECUCAO_RAPIDA.md)** - Como executar o sistema

---

## 📖 Documentação Principal (Raiz)

### Para Usuários
- **[README.md](README.md)** - Documentação principal do projeto
- **[LEITURA_5MIN.md](LEITURA_5MIN.md)** - Introdução rápida ao sistema
- **[GUIA_EXECUCAO_INTEGRAGAL.md](GUIA_EXECUCAO_INTEGRAGAL.md)** - Guia completo de execução
- **[GUIA_EXECUCAO_RAPIDA.md](GUIA_EXECUCAO_RAPIDA.md)** - Guia de execução simplificado
- **[README_VISUALIZADOR_PLACA.md](README_VISUALIZADOR_PLACA.md)** - Documentação do visualizador de placas

### Para Desenvolvedores
- **[TODO.md](TODO.md)** - Lista de tarefas e melhorias planejadas
- **[INSTRUCOES_INTEGRAGAL.md](INSTRUCOES_INTEGRAGAL.md)** - Instruções técnicas do sistema
- **[INSTRUCOES_DEPLOY.md](INSTRUCOES_DEPLOY.md)** - Guia de deploy e instalação

### Manutenção
- **[LIMPEZA_ARQUIVOS.md](LIMPEZA_ARQUIVOS.md)** - Relatório de limpeza e organização

---

## 📁 Documentação Técnica (/docs)

### Manuais e Guias
- **[docs/MANUAL_USUARIO.md](docs/MANUAL_USUARIO.md)** - Manual completo do usuário
- **[docs/FAQ.md](docs/FAQ.md)** - Perguntas frequentes
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Solução de problemas
- **[docs/GUIA_INICIO_RAPIDO.md](docs/GUIA_INICIO_RAPIDO.md)** - Guia de início rápido

### Arquitetura e Desenvolvimento
- **[docs/ARQUITETURA_TECNICA.md](docs/ARQUITETURA_TECNICA.md)** - Arquitetura técnica do sistema
- **[docs/PADRAO_ENCODING.md](docs/PADRAO_ENCODING.md)** - Padrões de codificação

### Progresso e Fases
- **[docs/PROGRESSO_FASE2.md](docs/PROGRESSO_FASE2.md)** - Progresso da Fase 2
- **[docs/PROGRESSO_FASE3.md](docs/PROGRESSO_FASE3.md)** - Progresso da Fase 3
- **[docs/PROGRESSO_FASE4.md](docs/PROGRESSO_FASE4.md)** - Progresso da Fase 4

---

## 📚 Documentação Legacy (/docs/legacy)

Documentação de desenvolvimento e histórico do projeto, organizada por categoria:

### 🗂️ Histórico de Fases
**[docs/legacy/historico_fases/](docs/legacy/historico_fases/)**

Documentação das fases de desenvolvimento concluídas:
- Relatórios de conclusão das Fases 1-7
- Documentação de etapas específicas
- Logs de validação e migração
- Análises de fases concluídas

### 📊 Relatórios de Desenvolvimento
**[docs/legacy/relatorios_desenvolvimento/](docs/legacy/relatorios_desenvolvimento/)**

Relatórios técnicos e análises do processo de desenvolvimento:
- Análises consolidadas
- Auditorias de codificação
- Comparações antes/depois
- Correções e melhorias implementadas
- Mapas visuais de arquitetura
- Status de projeto

### 📋 Planejamento
**[docs/legacy/planejamento/](docs/legacy/planejamento/)**

Planos de implementação e documentação de design:
- Planos de fases (5, 6, 7)
- Guias de implementação
- Explicações de sistemas
- Fluxos detalhados
- Recomendações técnicas
- Índices de documentação antigos

### 🔧 Scripts de Migração
**[docs/legacy/scripts_migracao/](docs/legacy/scripts_migracao/)**

Scripts executados durante o desenvolvimento:
- Scripts de migração de dados
- Scripts de validação
- Ferramentas de integração

---

## 🧪 Testes (/tests)

- **[tests/conftest.py](tests/conftest.py)** - Configuração de testes
- **[tests/fixtures/](tests/fixtures/)** - Dados de teste
- **Diversos testes unitários e de integração** - Ver diretório /tests

---

## 📝 Scripts de Utilidade (Raiz)

### Scripts de Limpeza
- **[limpeza_prioridade_alta.ps1](limpeza_prioridade_alta.ps1)** - Remove arquivos temporários e de debug
- **[limpeza_logs_reports.ps1](limpeza_logs_reports.ps1)** - Limpa logs e reports antigos
- **[organizar_documentacao.ps1](organizar_documentacao.ps1)** - Organiza documentação em /docs/legacy

### Scripts de Execução
- **[run_alertas.py](run_alertas.py)** - Sistema de alertas
- **[run_dashboard.py](run_dashboard.py)** - Dashboard
- **[run_graficos.py](run_graficos.py)** - Gráficos
- **[run_historico.py](run_historico.py)** - Histórico
- **[run_visualizador.py](run_visualizador.py)** - Visualizador de placas

---

## 🔍 Como Encontrar Documentação

### Por Tipo de Usuário

**Novo Usuário / Operador:**
1. README.md → LEITURA_5MIN.md → GUIA_EXECUCAO_RAPIDA.md
2. docs/MANUAL_USUARIO.md
3. docs/FAQ.md

**Desenvolvedor Novo no Projeto:**
1. README.md → docs/ARQUITETURA_TECNICA.md
2. TODO.md
3. docs/legacy/planejamento/ (para entender decisões de design)

**Mantenedor / DevOps:**
1. INSTRUCOES_DEPLOY.md
2. docs/TROUBLESHOOTING.md
3. LIMPEZA_ARQUIVOS.md

**Pesquisador / Auditoria:**
1. docs/legacy/historico_fases/ (histórico completo)
2. docs/legacy/relatorios_desenvolvimento/ (análises técnicas)

### Por Tarefa

| Tarefa | Documentos |
|--------|-----------|
| **Instalar o sistema** | INSTRUCOES_DEPLOY.md |
| **Executar primeira análise** | GUIA_EXECUCAO_RAPIDA.md |
| **Resolver problema** | docs/TROUBLESHOOTING.md, docs/FAQ.md |
| **Entender arquitetura** | docs/ARQUITETURA_TECNICA.md |
| **Contribuir código** | TODO.md, docs/PADRAO_ENCODING.md |
| **Fazer deploy** | INSTRUCOES_DEPLOY.md |
| **Visualizar placa** | README_VISUALIZADOR_PLACA.md |
| **Limpeza de arquivos** | LIMPEZA_ARQUIVOS.md |

---

## 📌 Notas Importantes

### Estrutura Atualizada (10/12/2025)
- ✅ Documentação principal mantida na raiz para fácil acesso
- ✅ Documentação técnica em `/docs`
- ✅ Histórico e desenvolvimento em `/docs/legacy`
- ✅ Removidos arquivos temporários e de debug
- ✅ Organizada documentação de fases antigas

### Encoding
Todos os arquivos seguem o padrão **UTF-8 sem BOM**. Ver [docs/PADRAO_ENCODING.md](docs/PADRAO_ENCODING.md).

### Manutenção
Execute periodicamente os scripts de limpeza:
```powershell
.\limpeza_prioridade_alta.ps1 -DryRun  # Simular
.\limpeza_logs_reports.ps1 -DryRun     # Simular
```

---

## 🆘 Suporte

- **Issues**: Consulte TODO.md para problemas conhecidos
- **FAQ**: docs/FAQ.md
- **Troubleshooting**: docs/TROUBLESHOOTING.md

---

**Versão do Índice**: 1.0  
**Última Revisão**: 10/12/2025
