# Visualizador de Placa - Uso com CSV

## 📖 Descrição

Script para visualizar placas usando dados de arquivos CSV, especialmente o arquivo `tmp_df_norm_excerpt.csv` gerado pelo sistema.

## 🚀 Como Usar

### Uso Básico

```bash
python visualizar_placa_csv.py
```

Por padrão, carrega o arquivo `tmp_df_norm_excerpt.csv` no diretório atual.

### Especificar Arquivo CSV

```bash
python visualizar_placa_csv.py caminho/para/arquivo.csv
```

## 📋 Formato do CSV Esperado

O CSV deve ter as seguintes características:

- **Separador**: ponto-e-vírgula (`;`)
- **Encoding**: UTF-8
- **Colunas obrigatórias**:
  - `poco` ou `Poco`: Identificação dos poços (ex: "A1+A2", "B1+B2")
  - `amostra` ou `Amostra`: Código da amostra
  - `codigo` ou `Codigo`: Código da amostra (pode ser igual a amostra)

- **Colunas de resultados** (formato: `ALVO - R`):
  - `SC2 - R`, `HMPV - R`, `INFA - R`, etc.
  - Valores esperados: `"ALVO - 1"` (Detectado), `"ALVO - 2"` (Não Detectado), `"ALVO - 3"` (Inconclusivo)

- **Colunas de CT** (formato: `ALVO - CT`):
  - `SC2 - CT`, `HMPV - CT`, `INFA - CT`, etc.
  - Valores numéricos (aceita vírgula ou ponto como separador decimal)

- **Colunas opcionais de metadata**:
  - `usuario_analise`: Nome do usuário
  - `exame`: Nome do exame
  - `lote`: Número do lote
  - `arquivo_corrida`: Nome do arquivo de corrida
  - `data_hora_analise`: Data e hora da análise

## 🎯 Funcionalidades

### 1. Conversão Automática

- ✅ Converte vírgulas para pontos em valores CT
- ✅ Normaliza nomes de colunas
- ✅ Detecta tamanho de grupo automaticamente (pares, trios, quartetos)
- ✅ Extrai metadata do próprio CSV

### 2. Validação

- ✅ Verifica colunas essenciais
- ✅ Mostra informações do DataFrame carregado
- ✅ Exibe análise de CT disponíveis
- ✅ Debug detalhado da leitura

### 3. Visualização

- ✅ Abre visualizador interativo de placa
- ✅ Mostra status por cor (verde=ND, vermelho=Det, laranja=Inc)
- ✅ Permite edição de targets e CT
- ✅ Grupos visuais com bordas coloridas

## 📊 Exemplo de Saída

```
====================================================================================================
VISUALIZADOR DE PLACA - Carregando de CSV
====================================================================================================

📂 Carregando arquivo: tmp_df_norm_excerpt.csv
✅ Arquivo carregado com sucesso!
   Shape: 10 linhas x 29 colunas

🔄 Convertendo valores CT (vírgula → ponto)...
   ✅ 9 colunas CT convertidas

📊 Colunas disponíveis:
    1. data_hora_analise
    2. usuario_analise
    3. poco
    4. amostra
    ...

📋 Primeiras linhas do DataFrame:
   poco      amostra       codigo    SC2 - R  SC2 - CT  HMPV - R  HMPV - CT
0  A1+A2  422386149R  422386149R  SC2 - 2       NaN  HMPV - 2        NaN
1  B1+B2  422386266R  422386266R  SC2 - 2       NaN  HMPV - 2        NaN
...

📝 Metadata extraída:
   usuario: márcio
   extracao: 20251206-Placa1
   data: 06/12/2025 18:18

🔢 Tamanho de grupo detectado: 2 (baseado em 'A1+A2')

🖥️  Abrindo visualizador de placa...
```

## 🐛 Debug

O script gera logs detalhados incluindo:

- ✅ Colunas disponíveis no CSV
- ✅ Targets descobertos
- ✅ Análise de CT disponíveis por alvo
- ✅ Origem dos dados (qual coluna)
- ✅ Valores normalizados

## ⚠️ Problemas Comuns

### 1. Arquivo não encontrado
```
❌ Erro: Arquivo não encontrado: tmp_df_norm_excerpt.csv
```
**Solução**: Verifique se o arquivo existe no diretório atual ou especifique o caminho completo.

### 2. Valores CT como NaN
```
DEBUG CSV: Alvo=SC2, res_val='SC2 - 2', norm_res='ND'
  -> Origem CT: coluna 'SC2 - CT', valor=nan
```
**Solução**: O script agora converte automaticamente vírgulas para pontos. Certifique-se de usar a versão atualizada.

### 3. Colunas faltantes
```
⚠️  Colunas essenciais faltantes: ['poco', 'amostra']
```
**Solução**: O CSV deve conter pelo menos as colunas `poco`, `amostra` e `codigo`. O script tenta normalizar automaticamente nomes similares.

## 🔗 Arquivos Relacionados

- `services/plate_viewer.py`: Visualizador de placas
- `utils/dataframe_reporter.py`: Sistema de relatórios
- `test_normalize_result.py`: Testes de normalização de resultados

## 📝 Notas

- O visualizador é **interativo**: você pode clicar nos poços para ver detalhes
- É possível **editar** valores de target e CT diretamente na interface
- As mudanças podem ser **propagadas** para todo o grupo automaticamente
- O sistema **não salva** alterações automaticamente - use as opções de exportação se necessário
