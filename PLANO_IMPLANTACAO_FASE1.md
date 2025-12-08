# Plano de Implantacao - Fase 1 (Fundacao)

Data: 2025-12-07  
Versao: 1.0  
Status: Pronto para execucao

## Visao geral
- Objetivo: implementar autodeteccao de equipamento, registry de equipamentos e extratores especificos; integrar ao fluxo de mapeamento/analise.
- Duracao estimada: 2 semanas.
- Saidas: detector funcionando (>95% acuracia), registry carregado, extratores normalizando dados, integracao no fluxo de extracao, testes passando e doc atualizada.

## Cronograma resumido (Semana 1-2)
- Dia 1-2: Equipment Detector.
- Dia 3-4: Equipment Registry.
- Dia 5-7: Extractores especificos.
- Dia 8-9: Integracao no fluxo (busca_extracao + AnalysisService hook).
- Dia 10: Testes, ajustes e doc.

## Escopo detalhado e prompts por etapa

### 1.1 Equipment Detector (services/equipment_detector.py)
**Entregavel:** detectar equipamento a partir de XLSX, retornar top-3 matches com confianca e estrutura detectada; permitir override manual.

**Tarefas:**
- Ler XLSX, inspecionar headers, colunas nao vazias e linha de inicio de dados.
- Calcular match-score contra padroes conhecidos (7500, CFX96, QuantStudio) e ordenar.
- Validar requisitos (formato de well, presenca de Target/Cq, linha minima).
- Expor funcoes publicas: `detectar_equipamento`, `analisar_estrutura_xlsx`, `calcular_match_score`, `obter_padroes_conhecidos`.

**Prompt sugerido:**
```
Gere services/equipment_detector.py (~350-400 linhas) com:
- detectar_equipamento(caminho_arquivo) -> dict
- analisar_estrutura_xlsx(path) -> dict
- calcular_match_score(estrutura, padrao) -> float
- obter_padroes_conhecidos() -> list
Padroes: 
  7500 (headers Well/Sample Name/Target/Cq, col A-D, start 5, valida well A01),
  CFX96 (headers Bio-Rad, col A/E/F, start 3),
  QuantStudio (col B/D/E, start 8).
Saida detectar_equipamento: {equipamento, confianca, alternativas:[{equipamento, confianca}], estrutura_detectada:{coluna_well, coluna_target, coluna_ct, linha_inicio, headers}}.
Trate excecoes com mensagens claras; retorne top-3 matches ordenados.
```

### 1.2 Equipment Registry (services/equipment_registry.py)
**Entregavel:** registry mapeando equipamento -> padrao XLSX -> extrator/formatador.

**Tarefas:**
- Ler `banco/equipamentos.csv` (colunas: nome, modelo, fabricante, tipo_placa, xlsx_config JSON).
- Dataclass `EquipmentConfig` com campos de colunas, linha_inicio, validacoes, extrator_nome, formatador_nome.
- Metodos: `load()`, `get(nome)`, `registrar_novo(config)`, validacao minima de estrutura, cache em memoria.

**Prompt sugerido:**
```
Gere services/equipment_registry.py (~250-300 linhas) com:
- EquipmentConfig (nome, modelo, fabricante, tipo_placa, xlsx_estrutura dict, extrator_nome, formatador_nome)
- EquipmentRegistry: load() lendo banco/equipamentos.csv (xlsx_config em JSON), get(nome), registrar_novo(config), validacoes basicas (colunas obrigatorias, linha_inicio > 0), normalizacao de chave (case/acentos), logs de aviso em linhas invalidas.
```

### 1.3 Extractores especificos (services/equipment_extractors.py)
**Entregavel:** extrair XLSX conforme equipamento, normalizar para colunas padrao.

**Tarefas:**
- Funcoes: `extrair_7500`, `extrair_cfx96`, `extrair_quantstudio`, `extrair_generico`.
- Ler XLSX respeitando `config.xlsx_estrutura` (colunas, linha de inicio), validar colunas, normalizar para `bem`, `amostra`, `alvo`, `ct`.
- Converter CT para float, remover linhas vazias, validar formato de well e target nao nulo.

**Prompt sugerido:**
```
Gere services/equipment_extractors.py (~400-500 linhas) com funcoes extrair_7500/CFX96/QuantStudio/generico.
Cada extrator: usa config.xlsx_estrutura (coluna_well/sample/target/ct, linha_inicio), valida colunas, converte CT para float, normaliza nomes (bem, amostra, alvo, ct), remove vazios, garante well A01..H12 quando aplicavel. Lancar erros claros se colunas faltarem.
```

### 1.4 Integracao no fluxo de extracao (extracao/busca_extracao.py)
**Entregavel:** autodeteccao embutida no mapeamento; estado preenchido com equipamento/config/extrator.

**Tarefas:**
- Ao selecionar XLSX: chamar `equipment_detector.detectar_equipamento`, mostrar match/top-3 e permitir escolha manual.
- Carregar `EquipmentRegistry`, salvar em `app_state`: `equipamento_detectado`, `equipment_config`, `extrator_selecionado`.
- Manter heuristica A9:M17; adicionar validacao com config do equipamento.

**Prompt sugerido:**
```
Atualize extracao/busca_extracao.py para chamar detectar_equipamento apos o arquivo ser selecionado. Exiba dialog com melhor match e alternativas, botao Confirmar/Escolher outro. Ao confirmar, carregue EquipmentRegistry e grave no app_state: equipamento_detectado, equipment_config, extrator_selecionado. Se falhar, permitir override manual. Nao remova a heuristica A9:M17 existente.
```

### 1.5 Gancho no AnalysisService/UniversalEngine (preparacao F2)
**Entregavel:** usar equipamento/config detectados ao ler resultados.

**Tarefas:**
- `AnalysisService.executar_analise`: se `app_state.equipment_config` existir, usar o extrator especifico para o arquivo de resultados.
- Injetar `equipamento_detectado` e `equipment_config` em metadados/contexto do `UniversalEngine` (mesmo sem regras/fomulas ainda).

**Prompt sugerido:**
```
Ajuste AnalysisService.executar_analise para usar extrator especifico quando app_state.equipment_config estiver presente. Injetar equipamento_detectado/metadados no retorno. Manter compatibilidade: fallback para fluxo atual quando nao houver detecao.
```

### 1.6 Testes automatizados (Pytest)
**Arquivos:**
- `tests/test_equipment_detector.py`: casos 7500, CFX96, QuantStudio, scores, override manual.
- `tests/test_equipment_registry.py`: carga CSV, get(), registrar_novo(), validacao de estrutura.
- `tests/test_equipment_extractors.py`: normalizacao 7500/CFX/QuantStudio, validacoes, tipos CT, remove vazios, erros de coluna/linha.

**Prompt sugerido:**
```
Crie testes Pytest para detector, registry e extratores, usando fixtures XLSX minimas em tests/fixtures/. Cubra colunas faltantes e linha_inicio invalida, alem dos casos felizes descritos.
```

### 1.7 Documentacao
- Atualizar README ou criar guia rapido com: como rodar detector, como cadastrar novo equipamento, como funciona o fluxo de confirmacao na extraacao.
- Anotar criterios de aceitacao e como executar testes.

**Prompt sugerido:**
```
Atualize README.md (ou docs/Fase1.md) com: passos de uso do detector, como adicionar equipamentos no CSV, como funciona a confirmacao no mapeamento, como rodar pytest da fase 1, criterios de aceitacao.
```

## Critérios de aceitaçao (Fase 1)
- Autodeteccao com confianca >= 95% nos arquivos alvo.
- Registry carregado e `get` funcionando para equipamentos cadastrados.
- Extratores normalizam para (bem, amostra, alvo, ct) e validam estrutura.
- Integracao no `extracao/busca_extracao.py` preenchendo `app_state` com equipamento/config/extrator.
- Testes Pytest da fase 1 passando; doc atualizada.

## Riscos e mitigacoes
- Arquivos fora do padrao: permitir override manual e logar padrao nao reconhecido.
- Variacoes de headers: usar normalizacao (casefold/acentos) e fallback generico.
- Performance em arquivos grandes: limitar leituras a sheet/intervalo necessario.
- Manutencao de padroes: centralizar padroes em `obter_padroes_conhecidos` e no CSV do registry.

## Proximos passos
- Implementar Detector, Registry e Extratores usando os prompts acima.
- Integrar no fluxo de extracao e AnalysisService.
- Rodar testes; ajustar ate passar.
- Atualizar doc e sinalizar conclusao da Fase 1.
