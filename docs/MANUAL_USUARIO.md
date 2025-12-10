# 📘 Manual do Usuário - IntegRAGal

**Sistema Integrado de Análise de Resultados GAL**  
**Versão**: 1.0.0  
**Data**: Dezembro de 2025  
**Desenvolvido para**: Laboratórios de análise molecular

---

## 📑 Índice

1. [Introdução](#1-introdução)
2. [Instalação](#2-instalação)
3. [Primeiros Passos](#3-primeiros-passos)
4. [Interface Principal](#4-interface-principal)
5. [Módulo de Extração](#5-módulo-de-extração)
6. [Análise de Resultados](#6-análise-de-resultados)
7. [Sistema de Alertas](#7-sistema-de-alertas)
8. [Gráficos e Relatórios](#8-gráficos-e-relatórios)
9. [Exportação](#9-exportação)
10. [Envio para GAL](#10-envio-para-gal)
11. [Configurações](#11-configurações)
12. [Histórico e Auditoria](#12-histórico-e-auditoria)
13. [Casos de Uso](#13-casos-de-uso)
14. [Boas Práticas](#14-boas-práticas)
15. [Glossário](#15-glossário)

---

## 1. Introdução

### 1.1 O que é o IntegRAGal?

O **IntegRAGal** (Sistema Integrado de Análise de Resultados GAL) é uma aplicação desktop desenvolvida para automatizar e otimizar o processo de análise de resultados de PCR em tempo real, com foco em testes moleculares realizados em equipamentos QuantStudio.

### 1.2 Principais Funcionalidades

✅ **Detecção Automática de Equipamentos**
- Reconhece automaticamente QuantStudio 3, 5 e 7
- Extrai configurações e metadados dos arquivos
- Valida integridade dos dados

✅ **Análise Inteligente de Resultados**
- Aplicação automática de regras de validação
- Cálculo de estatísticas descritivas
- Detecção de outliers e anomalias
- Validação de controles positivos e negativos

✅ **Sistema de Alertas em Tempo Real**
- 9 tipos de alertas configuráveis
- Badge visual com contadores
- Categorização por prioridade
- Histórico completo de alertas

✅ **Visualização Gráfica Avançada**
- Gráficos de amplificação
- Histogramas de distribuição CT
- Gráficos de dispersão
- Análise de qualidade por placa

✅ **Exportação Profissional**
- Relatórios em PDF com gráficos
- Planilhas Excel completas
- Arquivos CSV para análise externa
- Formatação personalizada

✅ **Integração com GAL**
- Envio automático de resultados
- Validação antes do envio
- Rastreamento de status
- Logs detalhados

### 1.3 Requisitos do Sistema

**Mínimos**:
- Windows 10 ou superior
- Python 3.10+
- 4 GB RAM
- 500 MB espaço em disco
- Resolução: 1280x720

**Recomendados**:
- Windows 11
- Python 3.13
- 8 GB RAM
- 2 GB espaço em disco
- Resolução: 1920x1080

### 1.4 Arquivos Suportados

- **Excel** (.xlsx, .xls): Resultados do QuantStudio
- **CSV** (.csv): Dados de amplificação e resultados
- **Texto** (.txt): Logs e metadados

---

## 2. Instalação

### 2.1 Instalação Básica

1. **Descompacte o arquivo**:
   ```
   integragal-v1.0.zip → C:\IntegRAGal
   ```

2. **Navegue até o diretório**:
   ```powershell
   cd C:\IntegRAGal
   ```

3. **Execute o instalador** (primeira vez):
   ```powershell
   .\install.bat
   ```

4. **Aguarde a instalação** das dependências (~2-3 minutos)

5. **Pronto!** O sistema está instalado.

### 2.2 Instalação Manual

Se preferir controle total:

```powershell
# 1. Criar ambiente virtual
python -m venv venv

# 2. Ativar ambiente
.\venv\Scripts\Activate.ps1

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Verificar instalação
python -c "import customtkinter; print('OK')"
```

### 2.3 Primeira Execução

Execute o sistema:
```powershell
python main.py
```

Na primeira execução:
- ✅ Configurações padrão são criadas
- ✅ Estrutura de diretórios é gerada
- ✅ Banco de dados é inicializado
- ✅ Interface é aberta

---

## 3. Primeiros Passos

### 3.1 Tela de Login

Ao abrir o sistema, você verá a tela de autenticação:

```
┌─────────────────────────────────────┐
│         🔬 IntegRAGal v1.0          │
│                                     │
│  Usuário: [____________]            │
│  Senha:   [____________]            │
│                                     │
│        [ Entrar ] [ Sair ]          │
└─────────────────────────────────────┘
```

**Credenciais Padrão**:
- Usuário: `admin`
- Senha: `admin123`

⚠️ **Importante**: Altere a senha na primeira vez!

### 3.2 Interface Principal (Dashboard)

Após o login, você verá o **Dashboard**:

```
┌────────────────────────────────────────────────────┐
│ IntegRAGal                    [Alertas: 0] [⚙️] [❌]│
├────────────────────────────────────────────────────┤
│                                                    │
│  📊 ANÁLISES RECENTES          📈 ESTATÍSTICAS    │
│  ┌──────────────────┐          ┌───────────────┐  │
│  │ Nenhuma análise  │          │ Total: 0      │  │
│  │ realizada ainda  │          │ Hoje: 0       │  │
│  └──────────────────┘          │ Semana: 0     │  │
│                                └───────────────┘  │
│                                                    │
│  🔔 ALERTAS ATIVOS             📄 AÇÕES RÁPIDAS   │
│  ┌──────────────────┐          ┌───────────────┐  │
│  │ Nenhum alerta    │          │ [Nova Análise]│  │
│  │                  │          │ [Histórico]   │  │
│  └──────────────────┘          │ [Relatórios]  │  │
│                                └───────────────┘  │
│                                                    │
├────────────────────────────────────────────────────┤
│ Usuário: admin | v1.0.0 | 10/12/2025 10:30       │
└────────────────────────────────────────────────────┘
```

### 3.3 Navegação Básica

**Menu Superior**:
- 📊 **Dashboard**: Visão geral do sistema
- 📥 **Extração**: Importar dados de equipamentos
- 🔬 **Análise**: Processar e validar resultados
- 📈 **Gráficos**: Visualizações e estatísticas
- 📄 **Relatórios**: Exportar documentos
- 🌐 **GAL**: Envio para sistema GAL
- 🔔 **Alertas**: Centro de notificações
- 📚 **Histórico**: Análises anteriores
- ⚙️ **Configurações**: Preferências do sistema

**Atalhos de Teclado**:
- `Ctrl+D`: Dashboard
- `Ctrl+N`: Nova análise
- `Ctrl+E`: Exportar relatório
- `Ctrl+H`: Histórico
- `Ctrl+,`: Configurações
- `F1`: Ajuda

---

## 4. Interface Principal

### 4.1 Dashboard

O Dashboard é sua central de controle:

**Seções Principais**:

1. **Análises Recentes** (canto superior esquerdo)
   - Lista das últimas 5 análises
   - Status de cada análise
   - Data e hora de execução
   - Clique para visualizar detalhes

2. **Estatísticas** (canto superior direito)
   - Total de análises realizadas
   - Análises do dia
   - Análises da semana
   - Taxa de aprovação

3. **Alertas Ativos** (canto inferior esquerdo)
   - Alertas não lidos
   - Categorizados por tipo
   - Badge com contador
   - Clique para ver detalhes

4. **Ações Rápidas** (canto inferior direito)
   - Nova Análise: Iniciar processo
   - Histórico: Ver análises anteriores
   - Relatórios: Gerar documentos
   - Configurações: Ajustar sistema

### 4.2 Barra de Status

Na parte inferior da tela:

```
┌──────────────────────────────────────────────┐
│ Usuário: admin | v1.0.0 | 10/12/2025 10:30  │
│ Status: Pronto | Memória: 120MB             │
└──────────────────────────────────────────────┘
```

Informações exibidas:
- Nome do usuário logado
- Versão do sistema
- Data e hora atual
- Status da aplicação
- Uso de memória

### 4.3 Badge de Alertas

No canto superior direito:

```
[🔔 Alertas: 5]
```

- **Verde** (0): Nenhum alerta
- **Amarelo** (1-5): Poucos alertas
- **Vermelho** (>5): Muitos alertas pendentes

Clique para abrir o **Centro de Notificações**.

---

## 5. Módulo de Extração

### 5.1 Importar Dados

**Passo 1**: Clique em **📥 Extração** no menu

**Passo 2**: Selecione o arquivo de resultados
```
Formatos aceitos:
- .xlsx (Excel do QuantStudio)
- .xls (Excel legado)
- .csv (valores separados por vírgula)
```

**Passo 3**: O sistema detecta automaticamente:
- ✅ Tipo de equipamento (QuantStudio 3/5/7)
- ✅ Configuração da corrida
- ✅ Número de amostras
- ✅ Alvos detectados
- ✅ Metadados da placa

**Passo 4**: Mapeamento de placas
```
┌──────────────────────────────────────┐
│ MAPEAMENTO DE PLACAS                 │
├──────────────────────────────────────┤
│                                      │
│ Placa Detectada: P001234             │
│ Data: 10/12/2025                     │
│ Equipamento: QuantStudio 5           │
│                                      │
│ [✓] Mapear automaticamente           │
│ [ ] Mapear manualmente               │
│                                      │
│       [Continuar] [Cancelar]         │
└──────────────────────────────────────┘
```

### 5.2 Validação de Dados

O sistema valida automaticamente:

✅ **Estrutura do Arquivo**:
- Formato correto
- Colunas obrigatórias presentes
- Tipos de dados válidos

✅ **Integridade dos Dados**:
- Valores numéricos em CT
- Datas válidas
- Amostras sem duplicatas

✅ **Controles de Qualidade**:
- Controles positivos detectados
- Controles negativos verificados
- Curva padrão validada

**Se houver erros**:
```
┌──────────────────────────────────────┐
│ ⚠️ AVISOS DE VALIDAÇÃO               │
├──────────────────────────────────────┤
│                                      │
│ • 2 amostras com CT > 35             │
│ • 1 controle negativo amplificou     │
│ • Placa não está mapeada             │
│                                      │
│ Deseja continuar mesmo assim?        │
│                                      │
│       [Sim] [Não] [Detalhes]         │
└──────────────────────────────────────┘
```

### 5.3 Configuração de Extração

Em **⚙️ Configurações → Extração**:

- **Equipamento Padrão**: Pré-selecionar tipo
- **Auto-detectar**: Detectar automaticamente
- **Validar Placas**: Exigir placas mapeadas
- **Extrair Metadados**: Incluir informações extras
- **Formato de Data**: DD/MM/YYYY ou YYYY-MM-DD
- **Separador CSV**: Vírgula ou ponto-e-vírgula

---

## 6. Análise de Resultados

### 6.1 Visão Geral de Análise

Após a extração, você vê a **Tela de Análise**:

```
┌────────────────────────────────────────────────────┐
│ ANÁLISE DE RESULTADOS                             │
├────────────────────────────────────────────────────┤
│                                                    │
│ Placa: P001234        Data: 10/12/2025            │
│ Amostras: 96          Válidas: 92  Inválidas: 4   │
│                                                    │
│ ┌──────────────────────────────────────────────┐  │
│ │ ID    | Amostra | Alvo | CT    | Resultado   │  │
│ ├──────────────────────────────────────────────┤  │
│ │ A01   | 2024001 | N1   | 22.5  | Positivo    │  │
│ │ A02   | 2024002 | N1   | 28.3  | Positivo    │  │
│ │ A03   | 2024003 | N1   | Und   | Negativo    │  │
│ │ ...   | ...     | ...  | ...   | ...         │  │
│ └──────────────────────────────────────────────┘  │
│                                                    │
│ [Aplicar Regras] [Ver Gráficos] [Exportar]       │
└────────────────────────────────────────────────────┘
```

### 6.2 Aplicação de Regras

Clique em **[Aplicar Regras]** para executar validações:

**Regras Automáticas**:

1. **Validação de CT**:
   - CT < 15: Alerta de CT baixo
   - CT > 35: Alerta de CT alto
   - CT ausente (Und): Negativo

2. **Validação de Controles**:
   - Controle Positivo deve amplificar
   - Controle Negativo NÃO deve amplificar
   - Curva padrão dentro dos limites

3. **Detecção de Outliers**:
   - Método IQR (Interquartile Range)
   - Limite configurável (padrão: 1.5)
   - Marcação visual de outliers

4. **Validação Cruzada**:
   - Alvos múltiplos (N1, N2, RP)
   - Consistência entre réplicas
   - Validação de pares

**Resultado da Aplicação**:
```
┌──────────────────────────────────────┐
│ ✅ REGRAS APLICADAS COM SUCESSO      │
├──────────────────────────────────────┤
│                                      │
│ • 92 amostras validadas              │
│ • 4 amostras com alertas             │
│ • 2 outliers detectados              │
│ • Controles: OK                      │
│                                      │
│ 5 alertas foram gerados              │
│                                      │
│       [Ver Alertas] [Fechar]         │
└──────────────────────────────────────┘
```

### 6.3 Filtros e Busca

Use filtros para encontrar resultados específicos:

**Barra de Filtros**:
```
┌────────────────────────────────────────────────────┐
│ Busca: [___________] 🔍                            │
│                                                    │
│ Resultado: [Todos ▼] | CT: [Todos ▼] | Data: [...│
│                                                    │
│ [✓] Apenas com alertas  [ ] Apenas inválidas      │
└────────────────────────────────────────────────────┘
```

**Opções de Filtro**:
- **Busca por texto**: ID, nome da amostra
- **Resultado**: Positivo, Negativo, Inconclusivo
- **Faixa de CT**: 0-15, 15-25, 25-35, >35
- **Data**: Hoje, Semana, Mês, Personalizado
- **Com alertas**: Mostrar apenas amostras com problemas

### 6.4 Edição Manual

Para corrigir manualmente:

1. **Duplo clique** na linha da amostra
2. Modal de edição aparece:

```
┌──────────────────────────────────────┐
│ EDITAR AMOSTRA                       │
├──────────────────────────────────────┤
│                                      │
│ ID: A01                              │
│ Amostra: 2024001                     │
│ Alvo: N1                             │
│                                      │
│ CT: [22.5]                           │
│                                      │
│ Resultado: [Positivo ▼]              │
│                                      │
│ Observação:                          │
│ [____________________________]       │
│                                      │
│       [Salvar] [Cancelar]            │
└──────────────────────────────────────┘
```

3. **Salvar**: Alterações são registradas no histórico
4. **Auditoria**: Log completo de modificações

---

## 7. Sistema de Alertas

### 7.1 Tipos de Alertas

O sistema gera 9 tipos de alertas:

| Tipo | Prioridade | Descrição |
|------|------------|-----------|
| 🔴 **CT Alto** | Alta | CT > 35, próximo ao limite de detecção |
| 🟡 **CT Baixo** | Média | CT < 15, possível contaminação |
| 🔵 **Placa Não Mapeada** | Alta | Placa sem mapeamento no sistema |
| ⚪ **Amostra Inválida** | Média | Dados inconsistentes ou incompletos |
| 🟠 **Erro Extração** | Alta | Falha ao extrair dados do arquivo |
| 🟣 **Aviso Qualidade** | Média | Controles fora dos limites |
| 🔵 **Info Sistema** | Baixa | Informações gerais |
| 🟢 **Operação Sucesso** | Baixa | Operação concluída com sucesso |
| 🔴 **Erro Crítico** | Crítica | Erro que impede operação |

### 7.2 Centro de Notificações

Acesse via **🔔 Alertas** ou badge no topo:

```
┌────────────────────────────────────────────────────┐
│ CENTRO DE NOTIFICAÇÕES              [Marcar Lido] │
├────────────────────────────────────────────────────┤
│                                                    │
│ [Todos] [Não Lidos] [Críticos] [Avisos] [Infos]  │
│                                                    │
│ ┌──────────────────────────────────────────────┐  │
│ │ 🔴 CT Alto - Amostra 2024004                 │  │
│ │    CT 38.2 acima do limite (35.0)            │  │
│ │    10/12/2025 10:45 • Não resolvido          │  │
│ ├──────────────────────────────────────────────┤  │
│ │ 🟡 CT Baixo - Amostra 2024015                │  │
│ │    CT 12.1 abaixo do esperado (15.0)         │  │
│ │    10/12/2025 10:42 • Não lido               │  │
│ ├──────────────────────────────────────────────┤  │
│ │ 🟢 Operação Concluída                        │  │
│ │    Análise de P001234 finalizada             │  │
│ │    10/12/2025 10:40 • Lido                   │  │
│ └──────────────────────────────────────────────┘  │
│                                                    │
│ Total: 15 | Não lidos: 8 | Críticos: 2           │
└────────────────────────────────────────────────────┘
```

### 7.3 Ações com Alertas

**Marcar como Lido**:
- Clique no alerta → **[Marcar Lido]**
- Remove da contagem de não lidos
- Alerta permanece no histórico

**Resolver Alerta**:
- Clique no alerta → **[Resolver]**
- Adicione observação (opcional)
- Alerta marcado como resolvido

**Exportar Alertas**:
- Botão **[Exportar]** no topo
- Formatos: Excel, CSV, PDF
- Filtros aplicáveis

**Limpar Alertas Antigos**:
- Menu → **[Limpar Antigos]**
- Remove alertas >7 dias (configurável)
- Mantém críticos e não resolvidos

### 7.4 Configuração de Alertas

Em **⚙️ Configurações → Alertas**:

```
┌────────────────────────────────────────┐
│ CONFIGURAÇÕES DE ALERTAS               │
├────────────────────────────────────────┤
│                                        │
│ [✓] Habilitar Sistema de Alertas      │
│                                        │
│ Limites de CT:                         │
│   CT Alto:  [35.0] ────●──── 45       │
│   CT Baixo: [15.0] ──●──────── 25     │
│                                        │
│ Notificações:                          │
│   [✓] Mostrar popup                    │
│   [ ] Reproduzir som                   │
│   Duração: [5] segundos                │
│                                        │
│ Badge de Alertas:                      │
│   [✓] Mostrar contador                 │
│   [✓] Piscar quando houver novos       │
│                                        │
│       [Aplicar] [Resetar] [Fechar]    │
└────────────────────────────────────────┘
```

---

## 8. Gráficos e Relatórios

### 8.1 Tipos de Gráficos

**1. Curva de Amplificação**:
```
Fluorescência vs. Ciclo

     │    ╱
  F  │   ╱
  l  │  ╱
  u  │ ╱
  o  │╱
  r  │_________________
     0   10   20   30   40
           Ciclos
```
- Visualiza amplificação em tempo real
- Identifica threshold crossing
- Compara múltiplas amostras

**2. Histograma de CT**:
```
Distribuição de Valores CT

  N  │     ┌─┐
  º  │     │ │  ┌─┐
     │  ┌─┐│ │┌─┤ │
  A  │  │ ││ ││ │ │┌─┐
  m  │  │ ││ ││ │ ││ │
  o  │  │ ││ ││ │ ││ │
  s  │  │ ││ ││ │ ││ │
  t  │__│_││_││_│_││_│__
       15 20 25 30 35 40
             CT
```
- Mostra distribuição de CTs
- Identifica padrões anômalos
- Visualiza limites configurados

**3. Gráfico de Dispersão**:
```
CT vs. Quantidade

  C  │         ●
  T  │      ●
     │   ●
  4  │ ●
  0  │●
     │________________________
      1   10  100 1000 10000
           Quantidade
```
- Relaciona CT com quantidade
- Valida curva padrão
- Identifica outliers

**4. Mapa de Calor da Placa**:
```
    1  2  3  4  5  6  7  8
  ┌─────────────────────────┐
A │██ ░░ ░░ ██ ░░ ░░ ██ ░░ │
B │░░ ░░ ██ ░░ ░░ ██ ░░ ░░ │
C │░░ ██ ░░ ░░ ██ ░░ ░░ ██ │
  └─────────────────────────┘
  
  ██ CT < 25    ░░ CT > 25
```
- Visualiza toda a placa
- Identifica padrões espaciais
- Detecta contaminação cruzada

### 8.2 Geração de Gráficos

**Passo 1**: Navegue para **📈 Gráficos**

**Passo 2**: Selecione o tipo de gráfico

**Passo 3**: Configure opções:
```
┌────────────────────────────────────────┐
│ CONFIGURAR GRÁFICO                     │
├────────────────────────────────────────┤
│                                        │
│ Tipo: [Histograma CT ▼]               │
│                                        │
│ Dados:                                 │
│   Placa: [P001234 ▼]                  │
│   Alvo: [N1 ▼]                         │
│                                        │
│ Opções:                                │
│   [✓] Mostrar limites                  │
│   [✓] Incluir outliers                 │
│   [ ] Escala logarítmica               │
│                                        │
│ Cores:                                 │
│   Tema: [Padrão ▼]                     │
│                                        │
│       [Gerar] [Cancelar]               │
└────────────────────────────────────────┘
```

**Passo 4**: Visualize o gráfico

**Passo 5**: Exportar
- **Salvar Imagem**: PNG, JPG (alta resolução)
- **Copiar**: Para colar em documentos
- **Exportar Dados**: CSV com dados do gráfico

### 8.3 Relatórios Estatísticos

Acesse **📄 Relatórios → Estatísticas**:

```
┌────────────────────────────────────────────────────┐
│ RELATÓRIO ESTATÍSTICO - P001234                    │
├────────────────────────────────────────────────────┤
│                                                    │
│ Placa: P001234                                     │
│ Data: 10/12/2025                                   │
│ Equipamento: QuantStudio 5                         │
│ Operador: admin                                    │
│                                                    │
│ ─────────────────────────────────────────────────  │
│ RESUMO                                             │
│ ─────────────────────────────────────────────────  │
│                                                    │
│ Total de amostras: 96                              │
│ Amostras válidas: 92 (95.8%)                       │
│ Positivos: 48 (52.2%)                              │
│ Negativos: 44 (47.8%)                              │
│ Inconclusivos: 0 (0.0%)                            │
│                                                    │
│ ─────────────────────────────────────────────────  │
│ ESTATÍSTICAS DE CT                                 │
│ ─────────────────────────────────────────────────  │
│                                                    │
│ Média: 24.5 ± 5.2                                  │
│ Mediana: 23.8                                      │
│ Mínimo: 15.2                                       │
│ Máximo: 36.5                                       │
│ Coeficiente de Variação: 21.2%                     │
│                                                    │
│ Quartis:                                           │
│   Q1 (25%): 20.5                                   │
│   Q2 (50%): 23.8                                   │
│   Q3 (75%): 28.3                                   │
│                                                    │
│ Outliers: 2 detectados (2.2%)                      │
│                                                    │
│ ─────────────────────────────────────────────────  │
│ CONTROLES DE QUALIDADE                             │
│ ─────────────────────────────────────────────────  │
│                                                    │
│ Controle Positivo: ✅ CT 22.1 (esperado: <30)      │
│ Controle Negativo: ✅ Não detectado                │
│ Curva Padrão: ✅ R² = 0.998 (esperado: >0.99)      │
│                                                    │
└────────────────────────────────────────────────────┘

[Exportar PDF] [Exportar Excel] [Imprimir] [Fechar]
```

---

## 9. Exportação

### 9.1 Formatos de Exportação

O sistema oferece 3 formatos principais:

**1. PDF - Relatório Profissional**:
- Formatação completa
- Gráficos em alta resolução
- Tabelas organizadas
- Cabeçalho e rodapé
- Logo da instituição (opcional)
- Ideal para: Documentação oficial, arquivamento

**2. Excel - Planilha Detalhada**:
- Múltiplas abas
- Formatação condicional
- Fórmulas preservadas
- Filtros automáticos
- Gráficos interativos
- Ideal para: Análise posterior, compartilhamento

**3. CSV - Dados Brutos**:
- Compatibilidade universal
- Importação fácil
- Sem formatação
- Arquivo leve
- Ideal para: Análise externa, scripts, bancos de dados

### 9.2 Exportar Resultados

**Passo 1**: Após análise, clique em **📄 Exportar**

**Passo 2**: Configure exportação:
```
┌────────────────────────────────────────┐
│ EXPORTAR RESULTADOS                    │
├────────────────────────────────────────┤
│                                        │
│ Formato: [PDF ▼]                       │
│                                        │
│ Conteúdo:                              │
│   [✓] Tabela de resultados             │
│   [✓] Gráficos                         │
│   [✓] Estatísticas                     │
│   [✓] Alertas                          │
│   [ ] Dados brutos de amplificação     │
│                                        │
│ Opções PDF:                            │
│   Orientação: [Retrato ▼]              │
│   DPI: [300] ────●──── 600             │
│   [ ] Incluir logo                     │
│                                        │
│ Destino:                               │
│   [C:\Reports\P001234.pdf] [📁]        │
│                                        │
│       [Exportar] [Cancelar]            │
└────────────────────────────────────────┘
```

**Passo 3**: Aguarde processamento

**Passo 4**: Arquivo salvo!
```
┌────────────────────────────────────────┐
│ ✅ EXPORTAÇÃO CONCLUÍDA                │
├────────────────────────────────────────┤
│                                        │
│ Arquivo criado com sucesso:            │
│                                        │
│ C:\Reports\P001234.pdf                 │
│ Tamanho: 2.5 MB                        │
│                                        │
│ [Abrir Arquivo] [Abrir Pasta] [OK]    │
└────────────────────────────────────────┘
```

### 9.3 Exportação em Lote

Para exportar múltiplas análises:

**Passo 1**: **📚 Histórico → Selecionar Múltiplas**

**Passo 2**: `Ctrl+Click` para selecionar

**Passo 3**: **[Exportar Selecionados]**

**Passo 4**: Escolha formato e destino

**Resultado**: Arquivo ZIP com todas as exportações

### 9.4 Templates Personalizados

Crie templates de exportação:

**Configurações → Exportação → Templates**:

```
┌────────────────────────────────────────┐
│ GERENCIAR TEMPLATES                    │
├────────────────────────────────────────┤
│                                        │
│ Templates Disponíveis:                 │
│                                        │
│ • Relatório Completo (padrão)          │
│ • Relatório Simplificado               │
│ • Apenas Positivos                     │
│ • Apenas Alertas                       │
│                                        │
│ [+ Novo] [Editar] [Excluir] [Fechar]  │
└────────────────────────────────────────┘
```

---

## 10. Envio para GAL

### 10.1 Configurar Conexão

Primeira vez? Configure a conexão com GAL:

**Configurações → GAL**:
```
┌────────────────────────────────────────┐
│ CONFIGURAÇÃO GAL                       │
├────────────────────────────────────────┤
│                                        │
│ URL do Servidor:                       │
│ [https://gal.saude.gov.br]             │
│                                        │
│ Credenciais:                           │
│   Usuário: [________________]          │
│   Senha:   [________________]          │
│                                        │
│ Opções:                                │
│   [✓] Validar antes de enviar          │
│   [✓] Tentar reconectar automaticamente│
│   Timeout: [30] segundos               │
│   Tentativas: [3]                      │
│                                        │
│ [Testar Conexão] [Salvar] [Cancelar]  │
└────────────────────────────────────────┘
```

### 10.2 Enviar Resultados

**Passo 1**: Após análise validada, clique **🌐 Enviar para GAL**

**Passo 2**: Revisão antes do envio:
```
┌────────────────────────────────────────────────────┐
│ ENVIAR PARA GAL                                    │
├────────────────────────────────────────────────────┤
│                                                    │
│ Análise: P001234                                   │
│ Data: 10/12/2025                                   │
│                                                    │
│ ✅ 92 amostras válidas serão enviadas              │
│ ⚠️  4 amostras com alertas serão incluídas         │
│                                                    │
│ Alertas pendentes:                                 │
│   • 2 CT Alto                                      │
│   • 2 CT Baixo                                     │
│                                                    │
│ [ ] Incluir amostras com alertas                   │
│ [✓] Gerar log detalhado                            │
│                                                    │
│       [Enviar] [Cancelar]                          │
└────────────────────────────────────────────────────┘
```

**Passo 3**: Envio em progresso
```
Enviando para GAL...
[████████████████░░░░] 80% (73/92)

Amostra atual: 2024073
```

**Passo 4**: Resultado
```
┌────────────────────────────────────────┐
│ ✅ ENVIO CONCLUÍDO                     │
├────────────────────────────────────────┤
│                                        │
│ 92 amostras enviadas com sucesso       │
│ Tempo: 45 segundos                     │
│                                        │
│ Protocolo: GAL-2025-001234             │
│                                        │
│ [Ver Log] [OK]                         │
└────────────────────────────────────────┘
```

### 10.3 Rastreamento de Envios

**Histórico → Envios GAL**:

```
┌────────────────────────────────────────────────────┐
│ HISTÓRICO DE ENVIOS GAL                            │
├────────────────────────────────────────────────────┤
│                                                    │
│ Data       │ Placa   │ Status  │ Protocolo        │
│────────────┼─────────┼─────────┼──────────────────│
│ 10/12 10:45│ P001234 │ ✅ OK   │ GAL-2025-001234  │
│ 09/12 15:30│ P001233 │ ✅ OK   │ GAL-2025-001233  │
│ 09/12 09:15│ P001232 │ ⚠️ Parc │ GAL-2025-001232  │
│ 08/12 16:20│ P001231 │ ❌ Erro │ -                │
│                                                    │
│ [Detalhes] [Reenviar] [Exportar Log] [Fechar]    │
└────────────────────────────────────────────────────┘
```

**Status**:
- ✅ **Sucesso**: Todos os dados enviados
- ⚠️ **Parcial**: Alguns dados falharam
- ❌ **Erro**: Envio falhou completamente
- 🕒 **Pendente**: Aguardando processamento

### 10.4 Resolução de Problemas

**Erro de Conexão**:
```
┌────────────────────────────────────────┐
│ ❌ ERRO DE CONEXÃO                     │
├────────────────────────────────────────┤
│                                        │
│ Não foi possível conectar ao GAL       │
│                                        │
│ Possíveis causas:                      │
│ • Sem conexão com internet             │
│ • Servidor GAL indisponível            │
│ • Credenciais inválidas                │
│ • Firewall bloqueando                  │
│                                        │
│ [Verificar Conexão] [Configurações]    │
│ [Tentar Novamente] [Cancelar]          │
└────────────────────────────────────────┘
```

**Dados Rejeitados**:
```
┌────────────────────────────────────────┐
│ ⚠️ DADOS REJEITADOS                    │
├────────────────────────────────────────┤
│                                        │
│ 3 amostras foram rejeitadas pelo GAL   │
│                                        │
│ Motivos:                               │
│ • 2024045: Amostra já cadastrada       │
│ • 2024087: CPF inválido                │
│ • 2024091: Data fora do período        │
│                                        │
│ [Corrigir] [Ignorar] [Detalhes]        │
└────────────────────────────────────────┘
```

---

## 11. Configurações

### 11.1 Acessar Configurações

**Atalho**: `Ctrl+,` ou clique no ícone **⚙️**

### 11.2 Categorias de Configurações

**🎨 Aparência**:
- Modo de cor: Dark / Light / System
- Cor do tema: Blue / Green / Dark Blue
- Tamanho da fonte: 8-24pt
- Animações: On / Off
- Som de notificações: On / Off

**🔔 Alertas**:
- Habilitar sistema: On / Off
- Limite CT Alto: 25-45 (padrão: 35)
- Limite CT Baixo: 5-25 (padrão: 15)
- Mostrar popup: On / Off
- Badge com contador: On / Off

**📄 Exportação**:
- Formato padrão: PDF / Excel / CSV
- Incluir gráficos: On / Off
- Incluir estatísticas: On / Off
- DPI dos gráficos: 150-600
- Diretório padrão: [caminho]

**📥 Extração**:
- Equipamento padrão: QuantStudio 3/5/7
- Auto-detectar: On / Off
- Validar placas: On / Off
- Formato de data: DD/MM/YYYY
- Separador CSV: , ou ;

**🔬 Análise**:
- Aplicar regras automaticamente: On / Off
- Verificar qualidade: On / Off
- Detectar outliers: On / Off
- Método outliers: IQR / Z-Score
- Validação estrita: On / Off

**🌐 GAL**:
- Enviar automaticamente: On / Off
- Validar antes do envio: On / Off
- Timeout: 10-60 segundos
- Máximo de tentativas: 1-5

**💾 Sessão**:
- Salvar estado automaticamente: On / Off
- Restaurar sessão anterior: On / Off
- Intervalo de auto-save: 1-30 minutos
- Manter histórico por: 7-90 dias

**⚡ Performance**:
- Máximo de alertas na memória: 100-5000
- Limpar alertas antigos: 1-30 dias
- Usar cache: On / Off
- Tamanho do cache: 50-500 MB

**⌨️ Atalhos** (em desenvolvimento):
- Customizar atalhos de teclado

**🔧 Avançado**:
- Modo debug: On / Off
- Nível de log: DEBUG / INFO / WARNING / ERROR
- Máximo de threads: 1-16
- Verificar atualizações: On / Off

### 11.3 Exportar/Importar Configurações

**Exportar suas configurações**:
1. Configurações → Botão **[📤 Exportar]**
2. Escolha local: `minhas_configuracoes.json`
3. Salvo!

**Importar configurações**:
1. Configurações → Botão **[📥 Importar]**
2. Selecione arquivo `.json`
3. Confirme importação
4. Sistema reinicia com novas configurações

**Resetar configurações**:
1. Configurações → Botão **[🔄 Resetar Categoria]**
2. Ou **[🔄 Resetar Tudo]** para padrão completo
3. Confirme (⚠️ irreversível)

---

## 12. Histórico e Auditoria

### 12.1 Acessar Histórico

**Menu → 📚 Histórico** ou `Ctrl+H`

### 12.2 Visualizar Análises Anteriores

```
┌────────────────────────────────────────────────────┐
│ HISTÓRICO DE ANÁLISES                              │
├────────────────────────────────────────────────────┤
│                                                    │
│ [Hoje] [Semana] [Mês] [Todos] Busca: [_______] 🔍│
│                                                    │
│ Data       │ Placa   │ Amostras │ Status │ Ações  │
│────────────┼─────────┼──────────┼────────┼────────│
│ 10/12 10:45│ P001234 │ 96 (92✅)│ ✅ OK  │ [►][📄]│
│ 09/12 15:30│ P001233 │ 96 (95✅)│ ✅ OK  │ [►][📄]│
│ 09/12 09:15│ P001232 │ 96 (88✅)│ ⚠️ Av  │ [►][📄]│
│ 08/12 16:20│ P001231 │ 48 (45✅)│ ✅ OK  │ [►][📄]│
│                                                    │
│ Total: 127 análises | Período: Último mês         │
└────────────────────────────────────────────────────┘
```

**Ações**:
- **[►]**: Ver detalhes
- **[📄]**: Exportar relatório
- **[🗑️]**: Excluir (requer confirmação)

### 12.3 Detalhes de Análise

Clique em **[►]** para ver detalhes:

```
┌────────────────────────────────────────────────────┐
│ DETALHES DA ANÁLISE - P001234                      │
├────────────────────────────────────────────────────┤
│                                                    │
│ INFORMAÇÕES GERAIS                                 │
│ ─────────────────────────────────────────────────  │
│ Placa: P001234                                     │
│ Data: 10/12/2025 10:45                             │
│ Equipamento: QuantStudio 5                         │
│ Operador: admin                                    │
│ Duração: 2h 15min                                  │
│                                                    │
│ RESULTADOS                                         │
│ ─────────────────────────────────────────────────  │
│ Total de amostras: 96                              │
│ Válidas: 92 (95.8%)                                │
│ Positivos: 48 (52.2%)                              │
│ Negativos: 44 (47.8%)                              │
│                                                    │
│ CONTROLES                                          │
│ ─────────────────────────────────────────────────  │
│ Controle Positivo: ✅ CT 22.1                      │
│ Controle Negativo: ✅ Não detectado                │
│                                                    │
│ ALERTAS                                            │
│ ─────────────────────────────────────────────────  │
│ Total: 4                                           │
│ • 2 CT Alto                                        │
│ • 2 CT Baixo                                       │
│                                                    │
│ GAL                                                │
│ ─────────────────────────────────────────────────  │
│ Status: ✅ Enviado                                 │
│ Protocolo: GAL-2025-001234                         │
│ Data envio: 10/12/2025 11:00                       │
│                                                    │
│ [Ver Amostras] [Ver Gráficos] [Exportar] [Fechar] │
└────────────────────────────────────────────────────┘
```

### 12.4 Logs do Sistema

Acesse logs detalhados em:

**Configurações → Avançado → [Ver Logs]**

```
┌────────────────────────────────────────────────────┐
│ LOGS DO SISTEMA                                    │
├────────────────────────────────────────────────────┤
│                                                    │
│ [INFO] [DEBUG] [WARNING] [ERROR] [Todos]          │
│                                                    │
│ 10/12/2025 10:45:23 [INFO] Análise P001234 iniciada
│ 10/12/2025 10:45:25 [INFO] Dados extraídos: 96 amostras
│ 10/12/2025 10:47:10 [WARN] CT alto em A15: 36.2
│ 10/12/2025 10:48:05 [INFO] Regras aplicadas
│ 10/12/2025 10:48:30 [INFO] Exportação PDF concluída
│ 10/12/2025 11:00:15 [INFO] Envio GAL bem-sucedido
│                                                    │
│ [Exportar] [Limpar] [Atualizar] [Fechar]          │
└────────────────────────────────────────────────────┘
```

---

## 13. Casos de Uso

### 13.1 Caso 1: Rotina Diária

**Cenário**: Processar resultados de PCR do dia

1. **Chegar ao laboratório** (08:00)
2. **Abrir IntegRAGal** → Login
3. **Dashboard**: Ver resumo do dia anterior
4. **Importar resultados**: Arquivos do QuantStudio
5. **Validar**: Aplicar regras automáticas
6. **Revisar alertas**: Verificar amostras problemáticas
7. **Gerar relatório**: PDF para arquivo
8. **Enviar para GAL**: Transmitir resultados validados
9. **Arquivar**: Salvar documentação

**Tempo estimado**: 30-45 minutos por placa

### 13.2 Caso 2: Investigação de Controles

**Cenário**: Controle negativo amplificou

1. **Alerta gerado**: "🔴 Controle Negativo Positivo"
2. **Abrir análise**: Ver detalhes do controle
3. **Ver curva**: Analisar amplificação
4. **Comparar com placa**: Verificar outras amostras
5. **Decisão**:
   - Se contaminação: Invalidar placa
   - Se falso positivo: Documentar e liberar
6. **Registrar**: Adicionar observação
7. **Notificar**: Equipe de qualidade

### 13.3 Caso 3: Análise Retrospectiva

**Cenário**: Revisar resultados do último mês

1. **Histórico** → **[Último Mês]**
2. **Filtrar**: Por equipamento, operador, resultado
3. **Exportar dados**: CSV de todas as análises
4. **Análise externa**: Excel, R, Python
5. **Gráficos de tendência**: Variação de CT ao longo do tempo
6. **Relatório gerencial**: Estatísticas consolidadas
7. **Ações corretivas**: Se necessário

### 13.4 Caso 4: Treinamento de Novo Usuário

**Cenário**: Treinar novo operador

1. **Criar usuário**: Configurações → Usuários
2. **Tour guiado**: Demonstrar interface
3. **Análise exemplo**: Usar dados de teste
4. **Prática supervisionada**: Processar 2-3 placas
5. **Resolução de problemas**: Simular alertas
6. **Validação**: Verificar competência
7. **Certificação**: Registrar treinamento

---

## 14. Boas Práticas

### 14.1 Organização de Arquivos

**Estrutura recomendada**:
```
C:\IntegRAGal\
├── dados_brutos\
│   └── 2025\
│       └── 12\
│           ├── P001234_raw.xlsx
│           ├── P001235_raw.xlsx
│           └── ...
├── relatorios\
│   └── 2025\
│       └── 12\
│           ├── P001234_relatorio.pdf
│           ├── P001235_relatorio.pdf
│           └── ...
└── backups\
    └── 2025\
        └── 12\
            └── backup_20251210.zip
```

### 14.2 Workflow Recomendado

1. **Importar** → Validar estrutura
2. **Mapear** → Garantir rastreabilidade
3. **Analisar** → Aplicar regras
4. **Revisar** → Verificar alertas
5. **Validar** → Confirmar controles
6. **Exportar** → Gerar relatório
7. **Enviar** → Transmitir para GAL
8. **Arquivar** → Guardar documentação

### 14.3 Segurança de Dados

✅ **Backup regular**:
- Diário: Banco de dados
- Semanal: Arquivos completos
- Mensal: Backup externo

✅ **Controle de acesso**:
- Senhas fortes
- Trocar senhas periodicamente
- Usuários individuais (não compartilhar)

✅ **Auditoria**:
- Revisar logs semanalmente
- Verificar acessos suspeitos
- Documentar mudanças importantes

### 14.4 Manutenção

**Semanal**:
- Limpar alertas antigos
- Verificar espaço em disco
- Revisar logs de erro

**Mensal**:
- Atualizar sistema (se disponível)
- Backup completo
- Revisar configurações

**Anual**:
- Auditoria completa
- Retreinamento da equipe
- Validação do sistema

---

## 15. Glossário

**CT (Cycle Threshold)**: Número de ciclos de PCR necessários para detectar fluorescência acima do limiar. Valores menores indicam maior quantidade de material genético.

**Controle Positivo**: Amostra conhecida que deve amplificar, usada para validar que a reação está funcionando corretamente.

**Controle Negativo**: Amostra sem material genético, usada para detectar contaminação. Não deve amplificar.

**Curva Padrão**: Série de diluições conhecidas usadas para quantificar amostras desconhecidas.

**GAL (Gerenciador de Ambiente Laboratorial)**: Sistema do Ministério da Saúde para gerenciamento de resultados laboratoriais.

**Outlier**: Valor estatisticamente diferente do padrão, pode indicar erro ou amostra anômala.

**PCR em Tempo Real**: Técnica de amplificação e detecção simultânea de DNA/RNA.

**QuantStudio**: Linha de equipamentos de PCR em tempo real da Thermo Fisher Scientific.

**Threshold**: Limiar de fluorescência usado para determinar CT.

**Undetermined (Und)**: Resultado não determinado, nenhuma amplificação detectada.

---

## 📞 Suporte

**Desenvolvedor**: Marcio Pacheco Lab  
**Email**: suporte@integragal.com  
**Documentação**: https://docs.integragal.com  
**GitHub**: https://github.com/Marciopachecolab/IntegRAGal

---

**Última atualização**: Dezembro de 2025  
**Versão do documento**: 1.0.0
