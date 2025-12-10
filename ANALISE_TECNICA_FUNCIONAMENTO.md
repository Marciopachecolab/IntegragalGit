# 🔍 ANÁLISE TÉCNICA COMPLETA - SISTEMA INTEGRAGAL

## 📊 FLUXO COMPLETO: DA ANÁLISE À TRANSMISSÃO GAL

Este documento descreve **PASSO A PASSO** como o sistema IntegRAGal funciona para permitir que um usuário analise um exame de PCR e transmita os resultados para o sistema GAL (Gerenciador de Ambiente Laboratorial) do Ministério da Saúde.

---

## 🎯 VISÃO GERAL DO FLUXO

```
┌─────────────────────────────────────────────────────────────────┐
│                    USUÁRIO INICIA SISTEMA                       │
│                      python main.py                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PASSO 1: LOGIN E AUTENTICAÇÃO                                   │
│ • Usuario digita credenciais (admin/admin123)                   │
│ • autenticacao/auth_service.py valida contra banco/usuarios.csv │
│ • AppState.usuario_logado = "admin"                             │
│ • Interface principal carregada (ui/main_window.py)             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PASSO 2: MAPEAMENTO DA PLACA (Extração)                        │
│ • Usuário clica "1. Mapeamento da Placa"                       │
│ • extracao/busca_extracao.py abre dialogo                      │
│ • Usuário seleciona planilha Excel de extração                 │
│ • Sistema busca intervalo A9:M17 (matriz 8x12 com A-H e 1-12) │
│ • Usuário escolhe tipo de kit (96, 48, 32 ou 24 poços)        │
│ • Sistema gera mapeamento (extracao/mapeamento_placas.py):     │
│   - 96 poços: 1:1 (1 extração → 1 análise)                    │
│   - 48 poços: 1:2 (1 extração → 2 análises) parte 1 ou 2     │
│   - 32 poços: 1:3 (1 extração → 3 análises) parte 1,2,3      │
│   - 24 poços: 1:4 (1 extração → 4 análises) parte 1,2,3,4    │
│ • DataFrame criado com colunas: Poco, Amostra, Codigo          │
│ • AppState.dados_extracao = DataFrame                           │
│ • AppState.parte_placa = 1 (ou 2, 3, 4)                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PASSO 3: REALIZAR ANÁLISE                                       │
│ • Usuário clica "2. Realizar Análise"                          │
│ • ui/menu_handler.py verifica se dados_extracao existe          │
│ • Dialog de seleção de exame aparece                           │
│   (services/analysis_service.listar_exames_disponiveis())      │
│ • Lista carregada de banco/exames_config.csv                    │
│ • Usuário seleciona exame (ex: "VR1e2 Biomanguinhos 7500")    │
│ • Usuário digita lote do kit (ex: "427")                       │
│ • AppState.exame_selecionado = "VR1e2 Biomanguinhos 7500"     │
│ • AppState.lote_kit = "427"                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PASSO 3.1: SELEÇÃO DO ARQUIVO DE RESULTADOS                    │
│ • Dialog de arquivo abre (filedialog.askopenfilename)          │
│ • Usuário seleciona arquivo do equipamento (.xlsx)             │
│   Exemplo: "QuantStudio_Results_20241210.xlsx"                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PASSO 3.2: DETECÇÃO AUTOMÁTICA DO EQUIPAMENTO                  │
│ • services/equipment_detector.py analisa arquivo                │
│ • Procura headers conhecidos: "Well", "Sample", "Target", "Ct" │
│ • Identifica padrões de QuantStudio 3/5/7                      │
│ • Calcula score de confiança (0-100%)                          │
│ • Retorna: {equipamento: "QuantStudio 5", confianca: 95}      │
│ • AppState.tipo_de_placa_detectado = "QuantStudio 5"          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PASSO 3.3: CARREGAMENTO DE CONFIGURAÇÕES                       │
│ • services/exam_registry.get_exam_cfg(exame) carrega:          │
│   - config/exams/{slug}.json (metadados específicos)           │
│   - banco/exames_config.csv (configuração geral)               │
│   - banco/regras.csv (regras de validação)                     │
│ • ExamConfig contém:                                            │
│   - nome_exame: "VRSRT"                                        │
│   - kit_codigo: "427"                                          │
│   - panel_tests_id: "1"                                        │
│   - export_fields: ["influenzaa", "influenzab", ...]          │
│   - controles: {"CN": [...], "CP": [...]}                     │
│   - alvos_detectar: ["INF A", "INF B", "SC2", ...]           │
│   - ct_thresholds: {detectado: 38, inconclusivo: 40}          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PASSO 3.4: PROCESSAMENTO UNIVERSAL (MOTOR DE ANÁLISE)          │
│ • services/universal_engine.UniversalEngine.processar()         │
│                                                                 │
│ ETAPA A: NORMALIZAÇÃO DO ARQUIVO                               │
│ • Lê arquivo Excel do equipamento                              │
│ • Normaliza nomes de colunas (remove espaços, acentos)         │
│ • Mapeia colunas: Well→Poco, Sample→Amostra, Ct→Ct_valor      │
│ • Remove linhas vazias                                          │
│                                                                 │
│ ETAPA B: INTEGRAÇÃO COM GABARITO                               │
│ • Faz merge com AppState.dados_extracao                        │
│ • Associa cada Well ao Codigo/Amostra correspondente           │
│ • Valida se todos os Wells esperados estão presentes           │
│                                                                 │
│ ETAPA C: APLICAÇÃO DE FÓRMULAS                                 │
│ • services/formula_parser.py processa fórmulas:                │
│   - CT_mean = MEAN(Ct replicatas)                             │
│   - CT_sd = STDEV(Ct replicatas)                              │
│   - Resultado = IF(CT < 38, "Detectado", "Não Detectado")    │
│ • Cria colunas calculadas no DataFrame                         │
│                                                                 │
│ ETAPA D: VALIDAÇÃO DE CONTROLES                                │
│ • Identifica poços CN (controle negativo) e CP (positivo)     │
│ • Valida segundo exam_cfg.controles:                           │
│   - CN deve ser "Não Detectado" (Ct > 38 ou undetermined)    │
│   - CP deve ser "Detectado" (Ct < 38)                         │
│ • Gera alertas se controles falharem                           │
│                                                                 │
│ ETAPA E: APLICAÇÃO DE REGRAS                                   │
│ • services/rules_engine.py aplica regras de banco/regras.csv:  │
│   - Ct < 15: "Outlier baixo - verificar contaminação"        │
│   - Ct 38-40: "Limítrofe - considerar reteste"               │
│   - SD > 0.5: "Alta variação entre replicatas"               │
│ • Adiciona coluna "Status_Validacao" e "Alertas"              │
│                                                                 │
│ ETAPA F: MAPEAMENTO DE RESULTADOS                              │
│ • Para cada alvo (INF A, INF B, SC2, etc):                    │
│   - Detectado → Código GAL "1"                                │
│   - Não Detectado → Código GAL "2"                            │
│   - Inconclusivo → Código GAL "3"                             │
│ • Cria colunas Resultado_INFA, Resultado_INFB, etc.            │
│                                                                 │
│ RESULTADO: DataFrame completo com todas validações             │
│ • AppState.resultados_analise = DataFrame processado            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PASSO 3.5: REGISTRO EM HISTÓRICO                               │
│ • db/db_utils.salvar_historico_processamento() grava em CSV:   │
│   - Arquivo: reports/historico_analises.csv                    │
│   - Colunas: data_hora, analista, exame, lote_kit, amostra,   │
│     codigo, poco, ct_value, resultado, status_validacao,       │
│     status_gal, equipamento, alvos_detectados                  │
│ • Status GAL inicial: "analizado e nao enviado"                │
│ • Cada linha = 1 amostra + 1 alvo                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PASSO 4: VISUALIZAÇÃO DOS RESULTADOS                           │
│ • Usuário clica "3. Visualizar e Salvar Resultados"           │
│ • interface/visualizador_exame.py carrega dados                │
│ • Exibe tabela interativa com:                                 │
│   - Coluna "Selecionado" (checkbox ✓ para exportar)          │
│   - Codigo, Amostra, Poco, Alvos detectados, Ct, Resultado    │
│   - Status de validação (✅ Válida, ⚠️ Aviso, ❌ Inválida)    │
│   - Alertas (se houver)                                        │
│ • Gráficos de qualidade:                                       │
│   - Distribuição de Ct por alvo                               │
│   - Controles CN/CP visualizados                               │
│ • Usuário marca amostras para exportar (padrão: todas ✓)      │
│ • Filtros automáticos:                                         │
│   - CN/CP NÃO são marcados (tipo_nao_enviavel)               │
│   - Códigos não-numéricos NÃO são marcados                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PASSO 5: EXPORTAÇÃO PARA FORMATO GAL                           │
│ • Usuário clica botão "Exportar CSV para GAL"                 │
│ • exportacao/exportar_resultados.py executado                  │
│                                                                 │
│ FILTRAGEM DE AMOSTRAS:                                         │
│ • Apenas linhas com Selecionado = "✓"                         │
│ • Remove controles CN/CP automaticamente                       │
│ • Remove códigos não-numéricos                                 │
│                                                                 │
│ FORMATAÇÃO GAL (main._formatar_para_gal):                      │
│ • Converte DataFrame para layout esperado pelo GAL:            │
│   ┌─────────────────┬──────────────────────────────────────┐   │
│   │ Coluna GAL      │ Origem                               │   │
│   ├─────────────────┼──────────────────────────────────────┤   │
│   │ codigoAmostra   │ Codigo (ex: "12345")                │   │
│   │ codigo          │ Codigo                               │   │
│   │ requisicao      │ "" (vazio)                          │   │
│   │ paciente        │ "" (vazio)                          │   │
│   │ exame           │ cfg.nome_exame ("VRSRT")            │   │
│   │ metodo          │ "RTTR" (fixo)                       │   │
│   │ registroInterno │ Codigo                               │   │
│   │ kit             │ cfg.kit_codigo ("427")              │   │
│   │ reteste         │ "" (vazio)                          │   │
│   │ loteKit         │ lote_kit digitado pelo usuário      │   │
│   │ dataProcessamento│ Data atual (DD/MM/YYYY)            │   │
│   │ valorReferencia │ "" (vazio)                          │   │
│   │ observacao      │ "" (vazio)                          │   │
│   │ painel          │ cfg.panel_tests_id ("1")            │   │
│   │ resultado       │ "" (vazio base)                     │   │
│   │ influenzaa      │ "1", "2" ou "3" (mapeado)          │   │
│   │ influenzab      │ "1", "2" ou "3" (mapeado)          │   │
│   │ coronavirusncov │ "1", "2" ou "3" (mapeado)          │   │
│   │ ... (outros)    │ Conforme cfg.export_fields          │   │
│   └─────────────────┴──────────────────────────────────────┘   │
│                                                                 │
│ MAPEAMENTO DE ALVOS (por alvo no painel):                      │
│ • Sistema busca coluna "Resultado_{ALVO}" no DataFrame         │
│ • Exemplo: "Resultado_INFA" → coluna GAL "influenzaa"         │
│ • Valores convertidos:                                          │
│   - "Detectado" / "Detectável" / "POS" → "1"                  │
│   - "Não Detectado" / "ND" / "NEG" → "2"                      │
│   - "Inconclusivo" / "" → "3"                                  │
│                                                                 │
│ EXEMPLO DE LINHA EXPORTADA:                                    │
│ 12345,,,"VRSRT","RTTR",12345,"427",,"LOT123","10/12/2024",    │
│ ,,"1","2","1","2",...                                          │
│ (1 linha = 1 amostra com TODOS os alvos do painel)            │
│                                                                 │
│ ARQUIVO SALVO:                                                  │
│ • Local: reports/GAL_Export_{timestamp}.csv                    │
│ • Encoding: UTF-8                                               │
│ • Separador: vírgula                                            │
│ • Atualiza histórico: status_gal = "exportado para csv"       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PASSO 6: ENVIO PARA GAL (TRANSMISSÃO WEB)                     │
│ • Usuário clica "4. Enviar para o GAL"                        │
│ • exportacao/envio_gal.py abre janela de integração            │
│ • Usuário seleciona arquivo CSV exportado no passo 5           │
│ • Usuário digita credenciais GAL (login/senha)                 │
│                                                                 │
│ ETAPA 6.1: INICIALIZAÇÃO DO NAVEGADOR                          │
│ • Selenium inicia Firefox em modo automatizado                 │
│ • exportacao/envio_gal.GalService.realizar_login():            │
│   - Acessa https://galteste.saude.sc.gov.br                   │
│   - Preenche campos: usuario, senha, módulo, laboratório      │
│   - Aguarda confirmação de login (elemento VERSAO-TOTAL)      │
│   - Navega para /laboratorio/                                  │
│                                                                 │
│ ETAPA 6.2: LEITURA E VALIDAÇÃO DO CSV                          │
│ • GalService.ler_csv_resultados() carrega CSV                  │
│ • Valida colunas obrigatórias: kit, painel, codigoAmostra     │
│ • Remove linhas vazias                                          │
│ • Normaliza códigos de amostra (remove .0, espaços)           │
│                                                                 │
│ ETAPA 6.3: BUSCA DE METADADOS NO GAL                           │
│ • GalService.buscar_metadados() faz requisição POST:           │
│   URL: /biomedicina/exame/listarGridJson                       │
│   Payload: {limit: 500, start: 0}                              │
│ • Para cada codigoAmostra no CSV:                              │
│   - Busca na resposta JSON do GAL                             │
│   - Extrai: codigo (ID interno GAL), requisicao, paciente     │
│ • Armazena mapeamento: {codigoAmostra → metadados GAL}        │
│                                                                 │
│ ETAPA 6.4: ENVIO AMOSTRA POR AMOSTRA                           │
│ • Para cada linha do CSV:                                      │
│   A. Constrói payload com metadados GAL + resultados:          │
│      {                                                         │
│        codigo: "123456" (ID GAL),                             │
│        requisicao: "REQ789",                                  │
│        codigoAmostra: "12345",                                │
│        kit: "427",                                            │
│        painel: "1",                                           │
│        loteKit: "LOT123",                                     │
│        dataProcessamentoFim: "10/12/2024",                    │
│        influenzaa: "1",                                       │
│        influenzab: "2",                                       │
│        ... (todos alvos do painel)                            │
│      }                                                         │
│                                                                 │
│   B. GalService.enviar_amostra() executa:                      │
│      1. Navega para página de entrada de resultados           │
│      2. Preenche campo codigoAmostra e clica "Pesquisar"     │
│      3. Aguarda grid de resultados carregar                    │
│      4. Clica no botão "Editar" da linha encontrada          │
│      5. Aguarda formulário de alvos abrir                     │
│      6. Para cada alvo (influenzaa, influenzab, etc):         │
│         - Localiza campo pelo ID do elemento                  │
│         - Preenche com valor ("1", "2" ou "3")               │
│      7. Preenche campos de kit, lote, data                    │
│      8. Clica botão "Salvar"                                  │
│      9. Valida mensagem de sucesso                            │
│                                                                 │
│   C. Tratamento de erros:                                      │
│      - Campo inválido → registra erro específico              │
│      - Amostra não encontrada → marca como "não localizada"  │
│      - Timeout → tenta retry (3x com backoff exponencial)    │
│                                                                 │
│   D. Atualiza histórico:                                       │
│      - reports/historico_analises.csv                         │
│      - status_gal = "enviado ao gal" (sucesso)               │
│      - status_gal = "erro no envio" (falha)                  │
│      - mensagem_gal = detalhes do erro/sucesso                │
│                                                                 │
│ ETAPA 6.5: RELATÓRIO FINAL                                     │
│ • Interface exibe resumo:                                      │
│   ✅ X amostras enviadas com sucesso                          │
│   ⚠️  Y amostras com avisos                                   │
│   ❌ Z amostras com erro                                      │
│ • Log detalhado salvo em: logs/gal_envio_{timestamp}.log      │
│ • Screenshots de erro salvos em: debug/                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PASSO 7: VERIFICAÇÃO E AUDITORIA                               │
│ • Usuário pode acessar "8. Relatórios"                        │
│ • interface/historico_analises.py exibe histórico completo:    │
│   - Todas análises realizadas                                  │
│   - Status de envio GAL                                        │
│   - Filtros por data, exame, status                           │
│   - Exportação para Excel/PDF                                  │
│ • Rastreabilidade completa:                                    │
│   - Quem analisou (analista)                                   │
│   - Quando analisou (timestamp)                                │
│   - Qual equipamento usou                                      │
│   - Quais resultados obteve                                    │
│   - Se foi enviado ao GAL                                      │
│   - Mensagens de erro/sucesso                                  │
└─────────────────────────────────────────────────────────────────┘

---

## 🔧 COMPONENTES TÉCNICOS DETALHADOS

### 1. MODELOS DE DADOS (models.py)

**AppState** - Armazena estado global da aplicação:
```python
class AppState:
    usuario_logado: str                     # "admin"
    dados_extracao: pd.DataFrame            # Gabarito de extração
    parte_placa: int                        # 1, 2, 3 ou 4
    resultados_analise: pd.DataFrame        # Resultados processados
    lote_kit: str                           # "427"
    exame_selecionado: str                  # "VR1e2 Biomanguinhos 7500"
    tipo_de_placa_detectado: str            # "QuantStudio 5"
    tipo_de_placa_config: EquipmentConfig   # Configuração do equipamento
    control_cn_wells: List[str]             # ["G11", "G12", "H11", "H12"]
    control_cp_wells: List[str]             # ["G9", "G10", "H9", "H10"]
```

### 2. AUTENTICAÇÃO (autenticacao/)

**auth_service.py** - Valida credenciais:
- Lê `banco/usuarios.csv`
- Compara hash de senha
- Registra sessão em `banco/sessoes.csv`
- Retorna `True/False`

**login.py** - Interface de login:
- Janela CTkToplevel
- Campos: usuário, senha
- Botão "Entrar" → chama auth_service
- Cria `AppState` após login bem-sucedido

### 3. EXTRAÇÃO E MAPEAMENTO (extracao/)

**busca_extracao.py** - Interface de mapeamento:
```python
BuscaExtracaoApp(CTkToplevel):
    _selecionar_planilha()              # Dialog para escolher Excel
    _encontrar_inicio_matriz(df)         # Busca A9:M17
    _validar_matriz()                    # Valida estrutura 8x12
    _gerar_mapeamento()                  # Chama mapeamento_placas.py
```

**mapeamento_placas.py** - Lógica de mapeamento:
```python
gerar_mapeamento_96() → List[Dict]
    # Retorna: [{"amostra": 1, "extracao": ("A1",), "analise": ("A1",)}, ...]

gerar_mapeamento_48(parte) → List[Dict]
    # Retorna: [{"amostra": 1, "extracao": ("A1",), "analise": ("A1", "A2")}, ...]
    # Parte 1: colunas 1-6 → análise 1-12
    # Parte 2: colunas 7-12 → análise 1-12

gerar_mapeamento_32(parte) → List[Dict]
    # 1 extração → 3 análises

gerar_mapeamento_24(parte) → List[Dict]
    # 1 extração → 4 análises
```

**Estrutura do DataFrame de extração:**
```
   Poco  Amostra    Codigo
0   A1   S001       12345
1   A2   S002       12346
2   A3   S003       12347
...
46  G11  CN         CN
47  G12  CN         CN
48  H11  CP         CP
49  H12  CP         CP
```

### 4. ANÁLISE (services/)

**analysis_service.py** - Orquestrador principal:
```python
class AnalysisService:
    def __init__(self, app_state: AppState):
        self.engine = UniversalEngine(app_state)
    
    def listar_exames_disponiveis() → List[str]:
        # Lê banco/exames_config.csv
        # Retorna: ["VR1e2 Biomanguinhos 7500", "ZDC Multiplex", ...]
    
    def executar_analise(app_state, parent_window, exame, lote):
        # 1. Valida dados_extracao existe
        # 2. Abre dialog para selecionar arquivo de resultados
        # 3. Detecta equipamento
        # 4. Carrega configuração do exame
        # 5. Chama universal_engine.processar()
        # 6. Salva resultados em app_state.resultados_analise
        # 7. Registra histórico
```

**universal_engine.py** - Motor de processamento:
```python
class UniversalEngine:
    def processar(caminho_resultados, exam_cfg, gabarito_extracao):
        # ETAPA 1: Normalização
        df_raw = pd.read_excel(caminho_resultados)
        df_norm = _normalize_columns(df_raw)
        
        # ETAPA 2: Integração com gabarito
        df_merged = pd.merge(df_norm, gabarito_extracao, on="Poco")
        
        # ETAPA 3: Aplicação de fórmulas
        for formula in exam_cfg.formulas:
            df_merged[formula.coluna] = avaliar_formula(df_merged, formula)
        
        # ETAPA 4: Validação de controles
        controles_validos = validar_controles(df_merged, exam_cfg.controles)
        
        # ETAPA 5: Aplicação de regras
        rules_result = aplicar_regras(df_merged, exam_cfg.regras)
        df_merged["Status_Validacao"] = rules_result.status
        df_merged["Alertas"] = rules_result.alertas
        
        # ETAPA 6: Mapeamento de resultados
        df_final = mapear_resultados_gal(df_merged, exam_cfg)
        
        return df_final
```

**equipment_detector.py** - Detecção de equipamento:
```python
class EquipmentDetector:
    def detectar_equipamento(caminho_arquivo):
        estrutura = analisar_estrutura_xlsx(caminho_arquivo)
        
        # Busca padrões conhecidos:
        # - QuantStudio: headers ["Well", "Sample Name", "Target Name", "Ct"]
        # - CFX96: headers ["Well", "Fluor", "Target", "Cq"]
        # - LightCycler: headers ["Pos", "Name", "Cp"]
        
        scores = []
        for padrao in self.padroes:
            score = calcular_match_score(estrutura, padrao)
            scores.append({"equipamento": padrao.nome, "confianca": score})
        
        scores.sort(key=lambda x: x["confianca"], reverse=True)
        return scores[0]  # Melhor match
```

**exam_registry.py** - Registro de exames:
```python
def get_exam_cfg(exame_slug: str) → ExamConfig:
    # Carrega config/exams/{slug}.json
    # Carrega banco/exames_config.csv
    # Merge das configurações
    # Retorna ExamConfig dataclass
```

**ExamConfig dataclass:**
```python
@dataclass
class ExamConfig:
    nome_exame: str                    # "VRSRT"
    kit_codigo: str                    # "427"
    panel_tests_id: str                # "1"
    export_fields: List[str]           # ["influenzaa", "influenzab", ...]
    controles: Dict[str, List[str]]    # {"CN": ["G11", "G12"], "CP": [...]}
    alvos_detectar: List[str]          # ["INF A", "INF B", "SC2", ...]
    ct_thresholds: Dict[str, float]    # {"detectado": 38, "inconclusivo": 40}
    formulas: List[Formula]            # Fórmulas de cálculo
    regras: List[Regra]                # Regras de validação
```

**formula_parser.py** - Processamento de fórmulas:
```python
def avaliar_formula(df: pd.DataFrame, formula: Formula):
    # Suporta:
    # - MEAN(coluna)
    # - STDEV(coluna)
    # - IF(condição, valor_true, valor_false)
    # - Operadores: <, >, <=, >=, ==, !=
    # Exemplo: "IF(Ct < 38, 'Detectado', 'Não Detectado')"
```

**rules_engine.py** - Motor de regras:
```python
def aplicar_regras(df: pd.DataFrame, regras: List[Regra]) → RulesResult:
    for regra in regras:
        if regra.condicao(row):
            row["Alertas"].append(regra.mensagem)
            row["Status_Validacao"] = regra.status
    
    # Regras típicas:
    # - Ct < 15: Outlier baixo
    # - Ct > 38: Limítrofe
    # - SD > 0.5: Alta variação
    # - CN detectado: Controle negativo falhou
    # - CP não detectado: Controle positivo falhou
```

### 5. EXPORTAÇÃO (exportacao/)

**exportar_resultados.py** - Exportação para CSV GAL:
```python
def exportar_resultados_gal(df_processado, lote_kit, exam_cfg):
    # 1. Filtra apenas linhas com Selecionado = "✓"
    df_export = df_processado[df_processado["Selecionado"] == "✓"]
    
    # 2. Remove controles CN/CP
    controles = exam_cfg.controles.keys()
    df_export = df_export[~df_export["Codigo"].isin(controles)]
    
    # 3. Remove códigos não-numéricos
    df_export = df_export[df_export["Codigo"].str.isdigit()]
    
    # 4. Formata para layout GAL
    df_gal = _formatar_para_gal(df_export, exam_cfg)
    
    # 5. Salva CSV
    caminho = f"reports/GAL_Export_{timestamp}.csv"
    df_gal.to_csv(caminho, index=False, encoding="utf-8")
    
    # 6. Atualiza histórico
    atualizar_historico_status(df_export, "exportado para csv")
```

**main._formatar_para_gal()** - Formatação GAL:
```python
def _formatar_para_gal(df, exam_cfg):
    df_out = pd.DataFrame()
    
    # Colunas fixas
    df_out["codigoAmostra"] = df["Codigo"]
    df_out["codigo"] = df["Codigo"]
    df_out["exame"] = exam_cfg.nome_exame
    df_out["kit"] = exam_cfg.kit_codigo
    df_out["painel"] = exam_cfg.panel_tests_id
    df_out["dataProcessamentoFim"] = datetime.now().strftime("%d/%m/%Y")
    
    # Colunas de alvos (dinâmicas por painel)
    for field in exam_cfg.export_fields:
        # Busca coluna Resultado_{ALVO} no DataFrame
        col_resultado = _find_result_col(df, field)
        
        if col_resultado:
            # Mapeia valores
            df_out[field] = df[col_resultado].map({
                "Detectado": "1",
                "Não Detectado": "2",
                "Inconclusivo": "3"
            })
        else:
            df_out[field] = ""
    
    return df_out
```

**envio_gal.py** - Transmissão web para GAL:
```python
class GalService:
    def __init__(self, logger_callback):
        self.base_url = "https://galteste.saude.sc.gov.br"
        self.panel_tests = {
            "1": ["influenzaa", "influenzab", ...],
            # Painel 1 = 29 alvos de vírus respiratórios
        }
    
    def realizar_login(self, driver, usuario, senha):
        driver.get(self.base_url)
        # Preenche campos de login
        driver.find_element(By.ID, "ext-comp-1008").send_keys(usuario)
        driver.find_element(By.ID, "ext-comp-1009").send_keys(senha)
        # Seleciona módulo e laboratório
        driver.find_element(By.ID, "ext-gen68").click()  # Login
        # Valida login bem-sucedido
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "VERSAO-TOTAL"))
        )
    
    def buscar_metadados(self, driver, codigos_amostra):
        url = self.base_url + "/biomedicina/exame/listarGridJson"
        metadados = {}
        
        start = 0
        while start < total:
            resp = driver.request("POST", url, data={
                "limit": 500, "start": start
            })
            
            for exame in resp.json()["dados"]:
                ca = exame["codigoAmostra"]
                if ca in codigos_amostra:
                    metadados[ca] = {
                        "codigo": exame["codigo"],  # ID interno GAL
                        "requisicao": exame["requisicao"],
                        "paciente": exame["paciente"]
                    }
            
            start += 500
        
        return metadados
    
    def enviar_amostra(self, driver, payload):
        # 1. Navega para página de entrada
        driver.get(self.base_url + "/laboratorio/entrada-resultados")
        
        # 2. Pesquisa amostra
        campo_busca = driver.find_element(By.ID, "campo-codigo-amostra")
        campo_busca.send_keys(payload["codigoAmostra"])
        driver.find_element(By.ID, "btn-pesquisar").click()
        
        # 3. Aguarda grid carregar
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "grid-resultados"))
        )
        
        # 4. Clica em "Editar"
        driver.find_element(By.CLASS_NAME, "btn-editar").click()
        
        # 5. Aguarda formulário abrir
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "form-alvos"))
        )
        
        # 6. Preenche alvos
        for alvo in self.panel_tests[payload["painel"]]:
            if alvo in payload and payload[alvo]:
                campo_id = f"campo-{alvo}"
                campo = driver.find_element(By.ID, campo_id)
                campo.clear()
                campo.send_keys(payload[alvo])
        
        # 7. Preenche campos adicionais
        driver.find_element(By.ID, "campo-kit").send_keys(payload["kit"])
        driver.find_element(By.ID, "campo-lote").send_keys(payload["loteKit"])
        driver.find_element(By.ID, "campo-data").send_keys(payload["dataProcessamentoFim"])
        
        # 8. Salva
        driver.find_element(By.ID, "btn-salvar").click()
        
        # 9. Valida sucesso
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "mensagem-sucesso"))
        )
        
        return {"status": "sucesso"}
```

### 6. HISTÓRICO E RASTREABILIDADE (db/)

**db_utils.py** - Gerenciamento de histórico:
```python
def salvar_historico_processamento(analista, exame, status, detalhes):
    # Se PostgreSQL habilitado:
    conn = get_postgres_connection()
    if conn:
        cursor.execute("""
            INSERT INTO historico_processos 
            (analista, exame, status, detalhes, data_hora)
            VALUES (%s, %s, %s, %s, NOW())
        """, (analista, exame, status, detalhes))
        conn.commit()
    
    # Sempre salva em CSV (backup local):
    df_historico = pd.read_csv("reports/historico_analises.csv")
    nova_linha = {
        "data_hora": datetime.now(),
        "analista": analista,
        "exame": exame,
        "status": status,
        "detalhes": detalhes
    }
    df_historico = pd.concat([df_historico, pd.DataFrame([nova_linha])])
    df_historico.to_csv("reports/historico_analises.csv", index=False)
```

**Estrutura do historico_analises.csv:**
```
data_hora,analista,exame,lote_kit,amostra,codigo,poco,alvo,ct_value,resultado,
status_validacao,status_gal,mensagem_gal,equipamento,alvos_detectados

2024-12-10 14:30:00,admin,VR1e2 Biomanguinhos 7500,427,S001,12345,A1,INF A,
22.5,Detectado,valida,enviado ao gal,Sucesso,QuantStudio 5,INF A;SC2

2024-12-10 14:30:00,admin,VR1e2 Biomanguinhos 7500,427,S001,12345,A1,INF B,
Undetermined,Não Detectado,valida,enviado ao gal,Sucesso,QuantStudio 5,INF A;SC2
...
```

### 7. INTERFACE (interface/ e ui/)

**main_window.py** - Janela principal:
```python
class App(ctk.CTk):
    def __init__(self):
        self.app_state = AppState()
        self.menu_handler = MenuHandler(self)
        
        # Cria interface
        self._criar_header()
        self._criar_menu()
        self._criar_status_bar()
```

**menu_handler.py** - Gerenciador de menu:
```python
class MenuHandler:
    def __init__(self, main_window):
        self.analysis_service = AnalysisService(main_window.app_state)
    
    def abrir_busca_extracao(self):
        # Abre BuscaExtracaoApp
        resultado = carregar_dados_extracao(self.main_window)
        if resultado:
            self.main_window.app_state.dados_extracao = resultado[0]
            self.main_window.app_state.parte_placa = resultado[1]
    
    def realizar_analise(self):
        # Valida que extração foi feita
        if not self.main_window.app_state.dados_extracao:
            messagebox.showerror("Execute o Mapeamento primeiro")
            return
        
        # Dialog de seleção de exame
        exame, lote = self._obter_detalhes_analise_via_dialogo()
        
        # Executa análise
        self.analysis_service.executar_analise(
            self.main_window.app_state,
            self.main_window,
            exame,
            lote
        )
```

**visualizador_exame.py** - Visualização de resultados:
```python
class VisualizadorExame(ctk.CTkToplevel):
    def __init__(self, master, dados_exame):
        self._criar_header()
        self._criar_tabela_resultados()
        self._criar_graficos()
        self._criar_botoes_acao()
    
    def _criar_tabela_resultados(self):
        # TreeView com colunas:
        # Selecionado | Codigo | Amostra | Poco | Alvos | Ct | Resultado | Status
        
        for _, row in self.df_resultados.iterrows():
            valores = [
                "✓" if row["Selecionado"] else "",
                row["Codigo"],
                row["Amostra"],
                row["Poco"],
                row["Alvos_Detectados"],
                row["Ct_mean"],
                row["Resultado"],
                row["Status_Validacao"]
            ]
            self.tree.insert("", "end", values=valores)
    
    def _criar_graficos(self):
        # Gráfico 1: Distribuição de Ct por alvo
        fig, ax = plt.subplots()
        for alvo in alvos:
            ct_values = df[df["Alvo"] == alvo]["Ct"]
            ax.hist(ct_values, label=alvo, alpha=0.5)
        ax.legend()
        
        # Gráfico 2: Controles CN/CP
        controles = df[df["Codigo"].isin(["CN", "CP"])]
        ax2.scatter(controles["Poco"], controles["Ct"], c=controles["Status"])
```

---

## 📝 EXEMPLO COMPLETO DE EXECUÇÃO

### Cenário: Análise de placa de Vírus Respiratórios

**1. PREPARAÇÃO**
```
Usuário tem:
- Planilha de extração: extracao_20241210.xlsx (A9:M17)
- Arquivo de resultados: quantstudio_20241210_VR.xlsx
- 48 amostras (Parte 1 da placa 96)
- Controles: CN em G11-G12, H11-H12 | CP em G9-G10, H9-H10
```

**2. MAPEAMENTO**
```
Input do usuário:
- Arquivo: extracao_20241210.xlsx
- Kit: 48 poços
- Parte: 1

Sistema gera:
AppState.dados_extracao = DataFrame com 48 linhas:
  A1→S001 (12345), A2→S002 (12346), ..., G11→CN, H11→CP
AppState.parte_placa = 1
```

**3. ANÁLISE**
```
Input do usuário:
- Exame: "VR1e2 Biomanguinhos 7500"
- Lote: "LOT123"
- Arquivo resultados: quantstudio_20241210_VR.xlsx

Sistema processa:
1. Detecta QuantStudio 5 (95% confiança)
2. Carrega exam_cfg:
   - nome_exame: "VRSRT"
   - kit_codigo: "427"
   - alvos: ["INF A", "INF B", "SC2", "ADV", "VSR", "MPV", "RV"]
3. Normaliza arquivo → 96 linhas (48 amostras × 2 replicatas)
4. Merge com gabarito → associa Wells a Códigos
5. Calcula Ct_mean, Ct_sd para cada amostra
6. Valida controles:
   - CN: todos Ct > 40 ✅
   - CP: todos Ct < 30 ✅
7. Aplica regras:
   - Amostra S015: Ct_sd = 0.8 → Alerta "Alta variação"
8. Mapeia resultados:
   - S001: INF A Detectado (Ct=22.5) → "1"
   - S001: INF B Não Detectado → "2"
   - S001: SC2 Detectado (Ct=25.0) → "1"
   
AppState.resultados_analise = DataFrame com 336 linhas (48 × 7 alvos)
```

**4. VISUALIZAÇÃO**
```
Interface mostra:
┌─────────────────────────────────────────────────────┐
│ ✓ │ 12345 │ S001 │ A1 │ INF A, SC2 │ 22.5 │ Det │ ✅ │
│ ✓ │ 12346 │ S002 │ A2 │ INF B      │ 28.0 │ Det │ ✅ │
│ ✓ │ 12347 │ S003 │ A3 │ -          │ -    │ ND  │ ✅ │
│ ⚠ │ 12348 │ S004 │ A4 │ SC2        │ 35.5 │ Det │ ⚠️ │
│   │ CN    │ CN   │ G11│ -          │ Und  │ ND  │ -  │
└─────────────────────────────────────────────────────┘

Alertas:
⚠️  S004: Ct limítrofe (35.5), considerar reteste
```

**5. EXPORTAÇÃO**
```
Usuário clica "Exportar CSV"

Sistema gera reports/GAL_Export_20241210_143000.csv:

codigoAmostra,codigo,requisicao,paciente,exame,metodo,registroInterno,kit,
reteste,loteKit,dataProcessamentoFim,valorReferencia,observacao,painel,
resultado,influenzaa,influenzab,coronavirusncov,adenovirus,vsincicialresp,
metapneumovirus,rinovirus

12345,12345,,,VRSRT,RTTR,12345,427,,LOT123,10/12/2024,,,1,,1,2,1,2,2,2,2
12346,12346,,,VRSRT,RTTR,12346,427,,LOT123,10/12/2024,,,1,,2,1,2,2,2,2,2
12347,12347,,,VRSRT,RTTR,12347,427,,LOT123,10/12/2024,,,1,,2,2,2,2,2,2,2
12348,12348,,,VRSRT,RTTR,12348,427,,LOT123,10/12/2024,,,1,,2,2,1,2,2,2,2

Nota: CN e CP NÃO aparecem no CSV (filtrados automaticamente)
```

**6. ENVIO GAL**
```
Usuário:
1. Clica "4. Enviar para o GAL"
2. Seleciona GAL_Export_20241210_143000.csv
3. Digita credenciais: usuario_lacen / senha123

Sistema executa:
[14:35:00] Iniciando Firefox...
[14:35:05] Login no GAL... ✅
[14:35:10] Lendo CSV: 48 amostras
[14:35:15] Buscando metadados GAL...
[14:35:20] Encontrados: 45/48 (3 não localizadas)
[14:35:25] Enviando amostra 12345...
  • Pesquisando no GAL... ✅
  • Editando formulário... ✅
  • Preenchendo alvos: influenzaa=1, coronavirusncov=1... ✅
  • Salvando... ✅
[14:35:30] Enviando amostra 12346... ✅
[14:35:35] Enviando amostra 12347... ✅
...
[14:50:00] CONCLUÍDO
  ✅ 45 amostras enviadas com sucesso
  ⚠️  3 amostras não localizadas no GAL
  
Relatório salvo: logs/gal_envio_20241210_143500.log
```

**7. HISTÓRICO ATUALIZADO**
```
reports/historico_analises.csv:

data_hora,analista,exame,lote_kit,codigo,status_gal,mensagem_gal
2024-12-10 14:30:00,admin,VR1e2,LOT123,12345,enviado ao gal,Sucesso
2024-12-10 14:30:00,admin,VR1e2,LOT123,12346,enviado ao gal,Sucesso
2024-12-10 14:30:00,admin,VR1e2,LOT123,12347,enviado ao gal,Sucesso
2024-12-10 14:30:00,admin,VR1e2,LOT123,12360,erro no envio,Amostra não localizada no GAL
```

---

## 🔐 SEGURANÇA E VALIDAÇÕES

### Camadas de Validação

1. **Autenticação**
   - Senha hasheada (SHA-256)
   - Sessão registrada com timestamp
   - Timeout após inatividade

2. **Validação de Dados de Entrada**
   - Matriz de extração: valida estrutura 8x12
   - Arquivo de resultados: valida headers obrigatórios
   - Códigos de amostra: valida formato numérico

3. **Controles de Qualidade**
   - CN deve ter Ct > threshold (38-40)
   - CP deve ter Ct < threshold (30-35)
   - Replicatas: SD < 0.5
   - Outliers: Ct < 15 ou Ct > 40

4. **Filtros de Exportação**
   - Remove controles CN/CP automaticamente
   - Remove códigos não-numéricos
   - Remove amostras não selecionadas pelo usuário

5. **Rastreabilidade**
   - Todo processamento registrado em histórico
   - Timestamp em cada ação
   - Analista identificado
   - Arquivos de entrada/saída salvos

---

## 🎓 CONCEITOS-CHAVE

### 1. Mapeamento de Placas

**Problema:** Placas de extração (96 poços) podem ser analisadas em múltiplas corridas

**Solução:** Sistema mapeia 1 poço de extração → N poços de análise
- Kit 96: análise completa (1:1)
- Kit 48: metade da placa (1:2 com replicatas)
- Kit 32: terço da placa (1:3 com triplicatas)
- Kit 24: quarto da placa (1:4 com quadruplicatas)

### 2. Motor Universal

**Desafio:** Suportar múltiplos equipamentos e protocolos

**Solução:** UniversalEngine usa configuração JSON (ExamConfig)
- Detecção automática de equipamento
- Normalização de colunas dinâmica
- Fórmulas configuráveis
- Regras de validação customizáveis

### 3. Painel de Alvos

**GAL usa painéis fixos** (ex: Painel 1 = 29 alvos de vírus respiratórios)

**Sistema mapeia alvos internos → campos GAL:**
```
Alvo Interno    → Campo GAL         → Valor
"INF A"         → "influenzaa"      → "1" (Detectado)
"INF B"         → "influenzab"      → "2" (Não Detectado)
"SC2"           → "coronavirusncov" → "1" (Detectado)
"ADV"           → "adenovirus"      → "2" (Não Detectado)
```

### 4. Histórico Dual

**PostgreSQL (opcional):** banco relacional completo
**CSV (obrigatório):** backup local sempre disponível

Garante que dados nunca sejam perdidos, mesmo se DB estiver offline.

---

## 🚨 PONTOS DE ATENÇÃO

### Problemas Comuns e Soluções

1. **Matriz de Extração Não Encontrada**
   - **Causa:** Intervalo A9:M17 não contém dados
   - **Solução:** Validar planilha, ajustar intervalo no código

2. **Equipamento Não Detectado**
   - **Causa:** Headers diferentes do esperado
   - **Solução:** Adicionar novo padrão em equipment_detector.py

3. **Controles Falham**
   - **Causa:** Contaminação ou erro de pipetagem
   - **Solução:** Sistema gera alerta, usuário decide se prossegue

4. **Amostra Não Localizada no GAL**
   - **Causa:** Código não existe no sistema GAL
   - **Solução:** Verificar se amostra foi cadastrada previamente

5. **Timeout no Envio GAL**
   - **Causa:** Conexão lenta ou sobrecarga do servidor
   - **Solução:** Sistema retenta automaticamente (3x com backoff)

---

## 📊 FLUXO DE DADOS SIMPLIFICADO

```
PLANILHA EXTRAÇÃO (Excel)
       ↓
   [Mapeamento]
       ↓
GABARITO (DataFrame: Poco → Codigo)
       ↓
       ↓ ← ARQUIVO RESULTADOS (Excel do equipamento)
       ↓
   [Motor Universal]
       ↓
RESULTADOS PROCESSADOS (DataFrame completo)
       ↓
   [Visualizador]
       ↓
SELEÇÃO DO USUÁRIO (marca amostras para enviar)
       ↓
   [Exportação]
       ↓
CSV FORMATO GAL
       ↓
   [Selenium + GAL Service]
       ↓
SISTEMA GAL (web form preenchido automaticamente)
       ↓
   [Confirmação]
       ↓
HISTÓRICO ATUALIZADO (status: "enviado ao gal")
```

---

## 🎯 RESUMO EXECUTIVO

**O QUE O SISTEMA FAZ:**
1. ✅ Carrega gabarito de extração (quem são as amostras)
2. ✅ Processa resultados de PCR (equipamento QuantStudio/CFX96)
3. ✅ Valida controles e aplica regras de qualidade
4. ✅ Formata dados no padrão exigido pelo GAL
5. ✅ Transmite automaticamente via web para o sistema do Ministério da Saúde
6. ✅ Registra tudo em histórico rastreável

**VANTAGENS:**
- ⚡ **Velocidade:** Processa 96 amostras em ~2 minutos
- 🎯 **Precisão:** Validações automáticas reduzem erros humanos
- 📝 **Rastreabilidade:** Todo processo registrado
- 🔄 **Integração:** Elimina digitação manual no GAL
- 🛡️ **Segurança:** Múltiplas camadas de validação

**TECNOLOGIAS:**
- Python 3.13
- CustomTkinter (interface)
- Pandas (processamento)
- Selenium (automação web)
- PostgreSQL/CSV (persistência)

---

## 📖 REFERÊNCIAS DE CÓDIGO

| Funcionalidade | Arquivo Principal | Linha Chave |
|---|---|---|
| Login | `autenticacao/auth_service.py` | `validar_credenciais()` |
| Mapeamento | `extracao/mapeamento_placas.py` | `gerar_mapeamento_48()` |
| Detecção Equip. | `services/equipment_detector.py` | `detectar_equipamento()` |
| Análise | `services/universal_engine.py` | `processar()` |
| Formatação GAL | `main.py` | `_formatar_para_gal()` |
| Envio GAL | `exportacao/envio_gal.py` | `GalService.enviar_amostra()` |
| Histórico | `db/db_utils.py` | `salvar_historico_processamento()` |

---

**Data da Análise:** 10 de dezembro de 2024  
**Versão do Sistema:** IntegRAGal v2.0  
**Analisado por:** GitHub Copilot (Claude Sonnet 4.5)

**Data da Análise**: 10 de dezembro de 2025  
**Versão Analisada**: 1.0.0  
**Foco**: Funcionamento, Arquitetura e Pontos Críticos

---

## 📊 SUMÁRIO EXECUTIVO

O **IntegRAGal** é um sistema desktop complexo para análise automatizada de resultados de PCR em tempo real (qPCR/RT-PCR) com integração ao sistema GAL do Ministério da Saúde. O sistema demonstra uma arquitetura modular bem estruturada, mas apresenta pontos críticos relacionados a acoplamento, gerenciamento de estado e detecção automática de equipamentos.

**Classificação Geral**: 
- **Maturidade**: Nível 3/5 (Funcional com pontos de melhoria)
- **Complexidade**: Alta (2.333 linhas no engine principal)
- **Qualidade de Código**: Boa (modularizado, comentado)
- **Testabilidade**: Média (testes presentes mas cobertura parcial)

---

## 🏗️ ARQUITETURA DO SISTEMA

### 1. VISÃO GERAL DA ARQUITETURA

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE APRESENTAÇÃO                    │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ main_window  │  │  interface/  │  │   ui/           │   │
│  │ (CTk)        │  │  componentes │  │   navigation    │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE SERVIÇOS                        │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   analysis   │  │    exam      │  │   equipment     │   │
│  │   service    │  │   registry   │  │   detector      │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   rules      │  │   formula    │  │    history      │   │
│  │   engine     │  │   parser     │  │    gal_sync     │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                       MOTOR CENTRAL                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │        UNIVERSAL ENGINE (2.333 linhas)                │  │
│  │  • Normalização de dados                              │  │
│  │  • Integração com gabarito de extração                │  │
│  │  • Aplicação de regras de validação                   │  │
│  │  • Geração de resultados                              │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     CAMADA DE DADOS                          │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  CSV Files   │  │  JSON Config │  │  Logs/Reports   │   │
│  │  (banco/)    │  │  (config/)   │  │  (logs/)        │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2. COMPONENTES PRINCIPAIS

#### 2.1 Estado da Aplicação (models.py)

**Modelo Centralizado de Estado (AppState)**

```python
class AppState:
    - usuario_logado: Optional[str]
    - dados_extracao: Optional[pd.DataFrame]
    - parte_placa: Optional[int]
    - resultados_analise: Optional[pd.DataFrame]
    - lote_kit: Optional[str]
    - exame_selecionado: Optional[str]
    - control_cn_wells: Optional[list[str]]
    - control_cp_wells: Optional[list[str]]
    - tipo_de_placa_detectado: Optional[str]
    - tipo_de_placa_config: Optional[object]
    - tipo_de_placa_selecionado: Optional[str]
```

**✅ Pontos Fortes**:
- Centralização do estado facilita debugging
- Métodos de reset organizados (`reset_analise_state`, `reset_extracao_state`)
- Tipagem clara com Optional

**⚠️ Pontos Fracos**:
- Estado mutável global (anti-pattern em sistemas complexos)
- Sem versionamento de estado
- Sem histórico de transições
- Dificulta testes unitários isolados

#### 2.2 Motor Universal (universal_engine.py)

**Componente Mais Crítico do Sistema (2.333 linhas)**

**Fluxo de Execução**:
```
executar_analise_universal()
  ↓
_ler_e_normalizar_arquivo()
  ├─ Detecta estrutura do arquivo
  ├─ Normaliza colunas (well, sample_name, target_name, ct)
  └─ Retorna DataFrame normalizado
  ↓
_integrar_com_gabarito_extracao()
  ├─ Busca gabarito em app_state
  ├─ Merge por well ou sample_name
  └─ Adiciona Codigo e Amostra
  ↓
_aplicar_regras_analise()
  ├─ Carrega regras do exam_registry
  ├─ Aplica rules_engine
  └─ Valida controles CN/CP
  ↓
_gerar_resultado_final()
  ├─ Pivot dos alvos
  ├─ Normaliza resultados
  └─ Adiciona metadados
```

**✅ Pontos Fortes**:
- Modularização clara em funções auxiliares
- Tratamento robusto de variações de encoding
- Suporte a múltiplos formatos de entrada
- Sistema de fallback para colunas ausentes
- Logging detalhado em cada etapa

**⚠️ Pontos Fracos**:
- **Tamanho excessivo** (2.333 linhas - violação do Single Responsibility Principle)
- **Acoplamento alto** com AppState
- **Complexidade ciclomática elevada** (muitos if/else aninhados)
- **Dificuldade de manutenção** (função monolítica)
- **Testes unitários difíceis** (muitas dependências)
- **Duplicação de código** (normalização de colunas em vários lugares)

**🔴 Pontos Críticos**:
```python
# Linha 390-460: Lógica complexa de detecção de gabarito
def _obter_gabarito_extracao(app_state: Any) -> Optional[pd.DataFrame]:
    # 7 tentativas diferentes de encontrar o gabarito
    # Varredura genérica por atributos do app_state
    # RISCO: Comportamento imprevisível se estrutura mudar
```

#### 2.3 Registro de Exames (exam_registry.py)

**Sistema Híbrido CSV + JSON**

**Estrutura**:
```
ExamConfig (dataclass)
├─ Metadados básicos (nome, slug, equipamento)
├─ Configuração de placa (tipo, esquema)
├─ Alvos e mapeamentos
├─ Faixas de CT
├─ Controles (CN/CP)
└─ Campos de exportação
```

**Carregamento em Camadas**:
1. **Base**: CSV em `banco/exames_config.csv`
2. **Sobrescrição**: JSON em `config/exams/<slug>.json`
3. **Merge**: JSON complementa/sobrescreve CSV

**✅ Pontos Fortes**:
- Flexibilidade (suporta CSV legacy + JSON moderno)
- Fácil adição de novos exames
- Configuração centralizada
- Validação de tipos com dataclass

**⚠️ Pontos Fracos**:
- **Dois formatos** aumentam complexidade
- **Sem validação de schema** JSON
- **Sem versionamento** de configurações
- **Potencial inconsistência** entre CSV e JSON

#### 2.4 Detecção de Equipamentos (equipment_detector.py)

**Detecção Automática por Padrões**

**Algoritmo**:
```python
detectar_equipamento(arquivo_xlsx)
  ↓
analisar_estrutura_xlsx()
  ├─ Lê todas as abas
  ├─ Identifica headers
  ├─ Mapeia colunas
  └─ Extrai keywords
  ↓
calcular_match_score()
  ├─ Score de headers (30%)
  ├─ Score de colunas (25%)
  ├─ Score de linha de início (15%)
  └─ Score de validações (30%)
  ↓
Retorna top-3 matches com confiança
```

**✅ Pontos Fortes**:
- Sistema de scoring ponderado
- Top-3 alternativas para confirmação
- Suporte a múltiplos equipamentos
- Wrapper para xlrd (compatibilidade com arquivos .xls antigos)

**⚠️ Pontos Fracos**:
- **Padrões hardcoded** (dificulta adição de novos equipamentos)
- **Sem machine learning** (depende de regras manuais)
- **Pode falhar com variações** de templates
- **Sem cache** de padrões detectados

**🔴 Pontos Críticos**:
```python
# Linha 168: analisar_estrutura_xlsx()
# Lê TODAS as abas do arquivo (performance)
# Pode falhar com arquivos grandes ou corrompidos
```

#### 2.5 Motor de Regras (rules_engine.py)

**Sistema de Validação Configurável**

**Tipos de Regras Suportadas**:
1. **Booleanas** - True/False simples
2. **Fórmulas** - Avaliação matemática
3. **Condicionais** - If-then
4. **Sequência** - Alvos obrigatórios
5. **Exclusão mútua** - Apenas um positivo
6. **Threshold** - Valor dentro de range

**Estrutura de Resultado**:
```python
RulesResult:
  ├─ status: "valida" | "invalida" | "aviso"
  ├─ validacoes: List[Validacao]
  ├─ mensagens_erro: List[str]
  ├─ mensagens_aviso: List[str]
  └─ tempo_execucao_ms: float
```

**✅ Pontos Fortes**:
- **Extensível** (fácil adicionar novos tipos)
- **Dataclasses** bem estruturadas
- **Timestamp** de validações
- **Sistema de impacto** (critico, alto, medio, baixo)

**⚠️ Pontos Fracos**:
- **Regras não são persistidas** (sempre recalculadas)
- **Sem histórico** de validações anteriores
- **Parsing de fórmulas** pode ser lento
- **Sem paralelização** de regras independentes

#### 2.6 Sincronização com GAL (history_gal_sync.py)

**Gerenciamento de Status de Envio**

**Fluxo**:
```
HistoricoGALSync
  ├─ marcar_enviado()
  │   └─ Atualiza status_gal = "enviado"
  ├─ marcar_falha_envio()
  │   └─ status_gal = "erro"
  └─ consultar_status()
      └─ Retorna registros por status
```

**Campos de Controle**:
- `id_registro` (UUID)
- `status_gal` (não enviado | enviado | erro)
- `data_hora_envio`
- `usuario_envio`
- `sucesso_envio`
- `detalhes_envio`

**✅ Pontos Fortes**:
- **UUID** garante unicidade
- **Rastreabilidade** completa
- **Validação** de arquivo CSV
- **Campos de auditoria**

**⚠️ Pontos Fracos**:
- **CSV como BD** (limitação de concorrência)
- **Lock de arquivo** não implementado
- **Sem transações** atômicas
- **Performance** degradada com muitos registros

---

## 🔄 FLUXO DE EXECUÇÃO COMPLETO

### Fluxo Principal do Usuário

```
1️⃣  AUTENTICAÇÃO
    └─ autenticacao/login.py
       ├─ Valida credenciais em banco/credenciais.csv
       └─ Armazena usuario_logado em AppState

2️⃣  MAPEAMENTO DA PLACA
    └─ extracao/busca_extracao.py
       ├─ User seleciona arquivo XLSX
       ├─ Sistema detecta matriz A9:M17
       ├─ User mapeia poços CN/CP
       ├─ User mapeia amostras (24/32/48/96 poços)
       └─ Salva em AppState.dados_extracao

3️⃣  ANÁLISE
    └─ services/analysis_service.py
       ├─ User seleciona exame + lote
       ├─ User seleciona arquivo de resultados
       ├─ equipment_detector.py detecta equipamento
       ├─ exam_registry.py carrega config do exame
       ├─ universal_engine.py processa dados
       │   ├─ Normaliza arquivo de resultados
       │   ├─ Integra com gabarito de extração
       │   ├─ Aplica regras de validação
       │   └─ Gera DataFrame final
       └─ Salva em AppState.resultados_analise

4️⃣  VISUALIZAÇÃO
    └─ interface/visualizador_exame.py
       ├─ Carrega AppState.resultados_analise
       ├─ Exibe tabela interativa
       ├─ Gráficos de qualidade
       └─ Permite seleção de amostras

5️⃣  EXPORTAÇÃO
    └─ exportacao/gal_export.py
       ├─ Formata resultados para GAL
       ├─ Gera CSV de exportação
       ├─ Registra em historico_analises.csv
       └─ Atualiza status_gal

6️⃣  ENVIO GAL
    └─ browser/selenium_gal.py
       ├─ Autentica no sistema GAL
       ├─ Navega até página de entrada
       ├─ Preenche formulário
       ├─ Submete dados
       └─ history_gal_sync.py atualiza status
```

---

## 💪 PONTOS FORTES DO SISTEMA

### 1. Arquitetura Modular
- ✅ **Separação clara de responsabilidades**
- ✅ **Serviços independentes** (analysis, exam_registry, equipment)
- ✅ **Camadas bem definidas** (UI, Services, Data)
- ✅ **Facilita manutenção** e evolução

### 2. Flexibilidade de Configuração
- ✅ **Sistema híbrido CSV + JSON** permite migração gradual
- ✅ **ExamConfig extensível** (fácil adicionar campos)
- ✅ **Configurações centralizadas** em config.json
- ✅ **Suporta múltiplos equipamentos** e protocolos

### 3. Robustez no Tratamento de Dados
- ✅ **Normalização de colunas** tolerante a variações
- ✅ **Fallback** para colunas ausentes
- ✅ **Tratamento de encoding** (UTF-8, CP1252, Latin1)
- ✅ **Validação de controles** CN/CP

### 4. Rastreabilidade
- ✅ **UUID** para cada análise
- ✅ **Histórico completo** em CSV
- ✅ **Status de envio** GAL
- ✅ **Logging detalhado** em todas as etapas

### 5. Interface Amigável
- ✅ **CustomTkinter** moderno
- ✅ **Feedback visual** em tempo real
- ✅ **Mensagens de erro** claras
- ✅ **Sistema de alertas** implementado

### 6. Suporte a Múltiplos Formatos
- ✅ **XLSX, XLS, CSV** de entrada
- ✅ **PDF, Excel, CSV** de saída
- ✅ **Compatibilidade** com arquivos legados

---

## ⚠️ PONTOS FRACOS DO SISTEMA

### 1. Gerenciamento de Estado

**Problema**: Estado global mutável
```python
# AppState é compartilhado por toda a aplicação
app_state = AppState()
# Qualquer módulo pode modificar qualquer atributo
app_state.dados_extracao = df  # Sem controle de acesso
```

**Impacto**:
- **Race conditions** potenciais
- **Dificuldade de debug** (quem modificou o quê?)
- **Testes unitários** complexos
- **Estado inconsistente** entre componentes

**Recomendação**:
```python
# Usar padrão Observer ou State Machine
class StateManager:
    def __init__(self):
        self._state = AppState()
        self._observers = []
    
    def set_dados_extracao(self, df):
        self._state.dados_extracao = df
        self._notify_observers("dados_extracao", df)
```

### 2. Tamanho do Universal Engine

**Problema**: Arquivo de 2.333 linhas
```
universal_engine.py: 2.333 linhas
├─ 150+ funções auxiliares
├─ Lógica de negócio misturada com I/O
└─ Dificuldade de navegação
```

**Impacto**:
- **Manutenção difícil**
- **Testes lentos**
- **Refatoração arriscada**
- **Onboarding** de desenvolvedores lento

**Recomendação**:
```
Dividir em módulos:
├─ normalization.py (normalização de dados)
├─ integration.py (integração com gabarito)
├─ validation.py (aplicação de regras)
└─ result_generator.py (geração de resultados)
```

### 3. CSV como Banco de Dados

**Problema**: Arquivos CSV para persistência
```python
# Sem controle de concorrência
df = pd.read_csv("logs/historico_analises.csv")
df = pd.concat([df, novo_registro])
df.to_csv("logs/historico_analises.csv")  # Sobrescreve
```

**Impacto**:
- **Perda de dados** se múltiplos acessos
- **Performance** degradada com muitos registros
- **Sem transações** atômicas
- **Sem índices** (busca linear)

**Recomendação**:
```python
# Migrar para SQLite (já planejado no config.json)
import sqlite3
conn = sqlite3.connect("integragal.db")
# Ou usar PostgreSQL para multi-usuário
```

### 4. Detecção de Equipamentos

**Problema**: Padrões hardcoded
```python
# equipment_detector.py
padroes = [
    EquipmentPattern(
        nome="QuantStudio 3",
        headers_esperados=["Well", "Target", "CT"],
        # ... padrão fixo
    )
]
```

**Impacto**:
- **Não extensível** sem editar código
- **Dificulta adição** de novos equipamentos
- **Sem aprendizado** de novos padrões
- **Manutenção custosa**

**Recomendação**:
```python
# Padrões em arquivo de configuração
padroes = carregar_padroes("config/equipment_patterns.yaml")

# Ou ML para detecção automática
from sklearn.ensemble import RandomForestClassifier
model.predict(estrutura_arquivo)
```

### 5. Tratamento de Erros

**Problema**: Try-except genéricos
```python
try:
    resultado = processar_dados(df)
except Exception:  # Muito genérico
    registrar_log("Erro", "Falha no processamento", "ERROR")
    return None
```

**Impacto**:
- **Erros silenciosos**
- **Dificulta debugging**
- **Sem recovery** automático
- **Logs pouco úteis**

**Recomendação**:
```python
class ProcessingError(Exception):
    """Erro específico de processamento"""
    
try:
    resultado = processar_dados(df)
except KeyError as e:
    raise ProcessingError(f"Coluna ausente: {e}")
except ValueError as e:
    raise ProcessingError(f"Valor inválido: {e}")
```

### 6. Testes

**Problema**: Cobertura parcial
```
tests/
├─ 30+ arquivos de teste
├─ Foco em testes de integração
└─ Poucos testes unitários
```

**Impacto**:
- **Regressões** não detectadas
- **Refatoração arriscada**
- **Confiança baixa** em mudanças
- **CI/CD difícil**

**Recomendação**:
```python
# Aumentar cobertura de testes unitários
# Meta: >80% coverage
pytest --cov=services --cov-report=html
```

---

## 🔴 PONTOS CRÍTICOS E RISCOS

### CRÍTICO 1: Perda de Dados no Histórico

**Local**: `history_gal_sync.py`

**Problema**:
```python
def _atualizar_registros(self, id_registros, ...):
    df = pd.read_csv(self.csv_path)  # Sem lock
    # ... modificações ...
    df.to_csv(self.csv_path)  # Sobrescreve
```

**Cenário de Falha**:
1. Usuário A inicia envio GAL
2. Usuário B inicia envio GAL (concorrente)
3. Ambos leem o mesmo CSV
4. Usuário A salva (sobrescreve)
5. Usuário B salva (sobrescreve A) ← **PERDA DE DADOS**

**Impacto**: 🔴 **ALTO** - Perda de registros de envio

**Mitigação Urgente**:
```python
import fcntl  # Unix
# ou
from filelock import FileLock  # Cross-platform

lock = FileLock("historico_analises.csv.lock")
with lock:
    df = pd.read_csv(self.csv_path)
    # ... modificações ...
    df.to_csv(self.csv_path)
```

### CRÍTICO 2: Estado Inconsistente Entre Etapas

**Local**: `models.py` + vários módulos

**Problema**:
```python
# Etapa 2: Mapeamento
app_state.dados_extracao = df_extracao

# Etapa 3: Análise
# User esquece de clicar "Mapeamento" novamente
# dados_extracao pode estar desatualizado
resultado = universal_engine(app_state, ...)
```

**Cenário de Falha**:
1. User mapeia placa A
2. User analisa (OK)
3. User mapeia placa B (sobrescreve dados_extracao)
4. User volta e re-analisa placa A ← **DADOS ERRADOS**

**Impacto**: 🔴 **ALTO** - Resultados incorretos

**Mitigação Urgente**:
```python
# Adicionar timestamp e validação
@dataclass
class AppState:
    dados_extracao: Optional[pd.DataFrame] = None
    dados_extracao_timestamp: Optional[datetime] = None
    
    def set_dados_extracao(self, df):
        self.dados_extracao = df
        self.dados_extracao_timestamp = datetime.now()
    
    def validar_dados_extracao(self, idade_maxima=timedelta(hours=1)):
        if self.dados_extracao_timestamp:
            if datetime.now() - self.dados_extracao_timestamp > idade_maxima:
                raise ValueError("Dados de extração expirados. Refaça o mapeamento.")
```

### CRÍTICO 3: Detecção Falsa de Gabarito

**Local**: `universal_engine.py:390-460`

**Problema**:
```python
def _obter_gabarito_extracao(app_state):
    # 7 tentativas diferentes de encontrar gabarito
    for attr, val in vars(app_state).items():
        if isinstance(val, pd.DataFrame):
            # Aceita QUALQUER DataFrame com coluna "poco"
            if "poco" in cols_lower:
                return val  # ← Pode retornar DataFrame errado!
```

**Cenário de Falha**:
1. app_state tem múltiplos DataFrames
2. Função pega o primeiro com coluna "poco"
3. Pode não ser o gabarito correto
4. Resultados incorretos

**Impacto**: 🔴 **MÉDIO** - Resultados potencialmente incorretos

**Mitigação**:
```python
# Nome padrão obrigatório
app_state.gabarito_extracao = df  # Nome fixo

# Ou marcar explicitamente
@dataclass
class ExtractionData:
    df: pd.DataFrame
    timestamp: datetime
    is_gabarito: bool = True
```

### CRÍTICO 4: Parsing de Fórmulas Inseguro

**Local**: `formula_parser.py`

**Problema**:
```python
def avaliar_formula(formula: str, variaveis: dict):
    # Se usar eval() é PERIGOSO
    resultado = eval(formula, {"__builtins__": {}}, variaveis)
```

**Cenário de Falha**:
1. Fórmula maliciosa: `"__import__('os').system('rm -rf /')"`
2. Execução de código arbitrário
3. Comprometimento do sistema

**Impacto**: 🔴 **CRÍTICO** - Vulnerabilidade de segurança

**Mitigação Urgente**:
```python
# Usar AST seguro
import ast

def avaliar_formula_segura(formula: str, variaveis: dict):
    tree = ast.parse(formula, mode='eval')
    # Validar apenas operações matemáticas permitidas
    for node in ast.walk(tree):
        if not isinstance(node, NODES_PERMITIDOS):
            raise ValueError(f"Operação não permitida: {type(node)}")
    return eval(compile(tree, '', 'eval'), {"__builtins__": {}}, variaveis)
```

### CRÍTICO 5: Performance com Arquivos Grandes

**Local**: `equipment_detector.py:168`

**Problema**:
```python
def analisar_estrutura_xlsx(caminho):
    # Lê TODAS as abas do arquivo
    wb = load_workbook(caminho, data_only=True)
    for sheet in wb.worksheets:  # Pode ser >100 abas
        # Processa tudo em memória
```

**Cenário de Falha**:
1. Arquivo XLSX com 50+ abas
2. Sistema trava por minutos
3. Memória insuficiente
4. Crash da aplicação

**Impacto**: 🟡 **MÉDIO** - UX ruim, possível crash

**Mitigação**:
```python
# Limitar abas processadas
MAX_SHEETS = 10

# Ou processar de forma lazy
from openpyxl import load_workbook
wb = load_workbook(caminho, read_only=True)
for i, sheet in enumerate(wb.worksheets):
    if i >= MAX_SHEETS:
        break
```

---

## 💡 SUGESTÕES DE MELHORIAS

### PRIORIDADE 1 (Curto Prazo - 1-2 semanas)

#### 1.1 Implementar Lock de Arquivo CSV
```python
# services/history_gal_sync.py
from filelock import FileLock

class HistoricoGALSync:
    def __init__(self, csv_path):
        self.csv_path = Path(csv_path)
        self.lock_path = self.csv_path.with_suffix('.lock')
    
    def _atualizar_registros(self, ...):
        with FileLock(str(self.lock_path), timeout=10):
            df = pd.read_csv(self.csv_path)
            # ... modificações ...
            df.to_csv(self.csv_path, index=False)
```

#### 1.2 Validação de Estado com Timestamps
```python
# models.py
from datetime import datetime, timedelta

@dataclass
class AppState:
    _dados_extracao: Optional[pd.DataFrame] = None
    _dados_extracao_ts: Optional[datetime] = None
    
    @property
    def dados_extracao(self):
        if self._dados_extracao_ts:
            age = datetime.now() - self._dados_extracao_ts
            if age > timedelta(hours=2):
                raise ValueError("Dados de extração expirados")
        return self._dados_extracao
    
    @dados_extracao.setter
    def dados_extracao(self, value):
        self._dados_extracao = value
        self._dados_extracao_ts = datetime.now()
```

#### 1.3 Parsing Seguro de Fórmulas
```python
# services/formula_parser.py
import ast
import operator

SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}

def avaliar_formula_segura(formula: str, variaveis: dict):
    tree = ast.parse(formula, mode='eval')
    # Validar AST
    _validar_ast_seguro(tree)
    # Avaliar com operadores permitidos
    return _avaliar_node(tree.body, variaveis)
```

### PRIORIDADE 2 (Médio Prazo - 1 mês)

#### 2.1 Refatorar Universal Engine
```
Dividir universal_engine.py em:

services/engine/
├── __init__.py
├── normalizer.py          # Normalização de dados
├── integrator.py          # Integração com gabarito
├── validator.py           # Aplicação de regras
├── result_generator.py    # Geração de resultados
└── coordinator.py         # Orquestra o fluxo
```

#### 2.2 Migrar para SQLite
```python
# services/database.py
import sqlite3
from contextlib import contextmanager

class Database:
    def __init__(self, db_path="integragal.db"):
        self.db_path = db_path
        self._criar_tabelas()
    
    def _criar_tabelas(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS historico_analises (
                    id_registro TEXT PRIMARY KEY,
                    exame TEXT NOT NULL,
                    data_analise TIMESTAMP NOT NULL,
                    usuario TEXT,
                    status_gal TEXT,
                    data_hora_envio TIMESTAMP,
                    INDEX idx_status (status_gal),
                    INDEX idx_data (data_analise)
                )
            """)
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
```

#### 2.3 Sistema de Cache
```python
# utils/cache.py
from functools import lru_cache
from datetime import datetime, timedelta

class CacheManager:
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key, max_age=timedelta(minutes=10)):
        if key in self._cache:
            age = datetime.now() - self._timestamps[key]
            if age < max_age:
                return self._cache[key]
        return None
    
    def set(self, key, value):
        self._cache[key] = value
        self._timestamps[key] = datetime.now()

# Uso
@cache_manager.cached(max_age=timedelta(minutes=15))
def get_exam_cfg(exame):
    return _carregar_exam_cfg(exame)
```

### PRIORIDADE 3 (Longo Prazo - 2-3 meses)

#### 3.1 Padrões de Equipamento Configuráveis
```yaml
# config/equipment_patterns.yaml
patterns:
  - nome: QuantStudio 3
    version: 1.0
    keywords: ["QuantStudio", "Applied Biosystems"]
    headers:
      required: ["Well", "Target Name", "CT"]
      optional: ["Reporter", "Quencher"]
    columns:
      well: ["Well", "Poço"]
      target: ["Target Name", "Alvo"]
      ct: ["CT", "C(t)", "Ct"]
    validation:
      min_rows: 10
      max_empty_ratio: 0.3
    scoring:
      headers: 30
      columns: 25
      linha_inicio: 15
      validacoes: 30
```

#### 3.2 Sistema de Eventos
```python
# core/events.py
from enum import Enum
from typing import Callable, Dict, List

class EventType(Enum):
    EXTRACAO_CONCLUIDA = "extracao_concluida"
    ANALISE_INICIADA = "analise_iniciada"
    ANALISE_CONCLUIDA = "analise_concluida"
    ENVIO_GAL_SUCESSO = "envio_gal_sucesso"
    ENVIO_GAL_FALHA = "envio_gal_falha"

class EventBus:
    def __init__(self):
        self._listeners: Dict[EventType, List[Callable]] = {}
    
    def subscribe(self, event_type: EventType, callback: Callable):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
    
    def publish(self, event_type: EventType, data: dict):
        for callback in self._listeners.get(event_type, []):
            callback(data)

# Uso
event_bus = EventBus()
event_bus.subscribe(EventType.ANALISE_CONCLUIDA, salvar_historico)
event_bus.subscribe(EventType.ANALISE_CONCLUIDA, enviar_notificacao)
```

#### 3.3 Machine Learning para Detecção
```python
# services/ml_detector.py
from sklearn.ensemble import RandomForestClassifier
import joblib

class MLEquipmentDetector:
    def __init__(self, model_path="models/equipment_classifier.pkl"):
        self.model = joblib.load(model_path)
    
    def extract_features(self, estrutura):
        return {
            'num_headers': len(estrutura['headers']),
            'num_rows': estrutura['max_row'],
            'has_ct_column': 'CT' in estrutura['headers'],
            'has_well_column': 'Well' in estrutura['headers'],
            # ... mais features
        }
    
    def predict(self, caminho_arquivo):
        estrutura = analisar_estrutura_xlsx(caminho_arquivo)
        features = self.extract_features(estrutura)
        equipamento = self.model.predict([features])[0]
        confianca = self.model.predict_proba([features]).max()
        return equipamento, confianca
```

---

## 📊 MÉTRICAS DE QUALIDADE

### Complexidade de Código

| Módulo | Linhas | Funções | Complexidade | Nota |
|--------|--------|---------|--------------|------|
| universal_engine.py | 2.333 | 150+ | 🔴 Alta | Refatorar |
| exam_registry.py | 617 | 20 | 🟢 Baixa | OK |
| equipment_detector.py | 648 | 15 | 🟡 Média | Melhorar |
| rules_engine.py | 629 | 25 | 🟡 Média | OK |
| main_window.py | 639 | 30 | 🟡 Média | OK |

### Cobertura de Testes (Estimada)

```
services/        ~40% ⚠️
extracao/        ~30% 🔴
interface/       ~20% 🔴
utils/           ~60% 🟡
core/            ~50% 🟡

TOTAL ESTIMADO: ~40% 🔴
META: >80% 🎯
```

### Dependências Externas

```
Principais:
├─ pandas (1.5+)          # Análise de dados
├─ openpyxl (3.0+)        # Leitura XLSX
├─ customtkinter (5.0+)   # Interface moderna
├─ selenium (4.0+)        # Automação web
├─ matplotlib (3.5+)      # Gráficos
└─ pyyaml (6.0+)          # Config YAML

Vulnerabilidades conhecidas: NENHUMA ✅
Atualizações pendentes: 3 bibliotecas 🟡
```

---

## 🎯 CONCLUSÃO E RECOMENDAÇÕES

### Avaliação Geral

O **IntegRAGal** é um sistema **funcional e bem estruturado**, demonstrando boa arquitetura modular e separação de responsabilidades. No entanto, apresenta **pontos críticos** que podem comprometer a integridade dos dados e a experiência do usuário em cenários de uso intenso.

### Classificação por Componente

| Componente | Qualidade | Urgência de Melhoria |
|-----------|-----------|----------------------|
| AppState | 🟡 Média | 🔴 Alta |
| Universal Engine | 🟡 Média | 🔴 Alta |
| Exam Registry | 🟢 Boa | 🟢 Baixa |
| Equipment Detector | 🟡 Média | 🟡 Média |
| Rules Engine | 🟢 Boa | 🟢 Baixa |
| History GAL Sync | 🔴 Baixa | 🔴 Crítica |
| Interface | 🟢 Boa | 🟢 Baixa |

### Roadmap de Melhorias

#### ⏰ SPRINT 1 (Semana 1-2) - CRÍTICO
1. ✅ Implementar lock de arquivo CSV
2. ✅ Validação de estado com timestamps
3. ✅ Parsing seguro de fórmulas
4. ✅ Limitar processamento de abas XLSX
5. ✅ Adicionar testes unitários críticos

#### ⏰ SPRINT 2 (Semana 3-4) - IMPORTANTE
1. 🔧 Refatorar Universal Engine (dividir em módulos)
2. 🔧 Implementar sistema de cache
3. 🔧 Migrar histórico para SQLite
4. 🔧 Melhorar tratamento de erros
5. 🔧 Aumentar cobertura de testes

#### ⏰ SPRINT 3 (Mês 2) - EVOLUTIVO
1. 🚀 Padrões de equipamento configuráveis
2. 🚀 Sistema de eventos
3. 🚀 Dashboard de monitoramento
4. 🚀 API REST (para integrações futuras)
5. 🚀 ML para detecção de equipamentos

### Principais Riscos Atuais

| # | Risco | Probabilidade | Impacto | Mitigação |
|---|-------|---------------|---------|-----------|
| 1 | Perda de dados no histórico | 🔴 Alta | 🔴 Crítico | Lock de arquivo |
| 2 | Estado inconsistente | 🟡 Média | 🔴 Alto | Validação timestamps |
| 3 | Injeção de código via fórmulas | 🟢 Baixa | 🔴 Crítico | AST seguro |
| 4 | Performance com arquivos grandes | 🟡 Média | 🟡 Médio | Limitar processamento |
| 5 | Detecção incorreta de equipamento | 🟡 Média | 🟡 Médio | Confirmar com usuário |

### Recomendação Final

O sistema está **pronto para produção em ambientes controlados** (single-user, baixo volume), mas **requer melhorias críticas** antes de ser usado em:
- ✅ Ambientes multi-usuário
- ✅ Alto volume de análises (>100/dia)
- ✅ Múltiplas instâncias concorrentes

**Priorizar**: Lock de arquivo CSV + Validação de estado + Parsing seguro

---

**Documento gerado em**: 10/12/2025  
**Versão**: 1.0  
**Próxima revisão**: Após implementação do Sprint 1
