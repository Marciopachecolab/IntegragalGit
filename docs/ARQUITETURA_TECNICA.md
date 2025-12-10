# 🏗️ ARQUITETURA TÉCNICA

**IntegRAGal - Documentação para Desenvolvedores**

---

## 📑 Índice

- [Visão Geral do Sistema](#visão-geral-do-sistema)
- [Arquitetura de Alto Nível](#arquitetura-de-alto-nível)
- [Módulos e Componentes](#módulos-e-componentes)
- [Fluxo de Dados](#fluxo-de-dados)
- [Camada de Persistência](#camada-de-persistência)
- [Sistema de Alertas](#sistema-de-alertas)
- [Interface Gráfica](#interface-gráfica)
- [Design Patterns Utilizados](#design-patterns-utilizados)
- [Extensibilidade](#extensibilidade)
- [Performance e Otimização](#performance-e-otimização)
- [Segurança](#segurança)
- [Testes](#testes)
- [Roadmap Técnico](#roadmap-técnico)

---

## Visão Geral do Sistema

### Propósito

IntegRAGal é um sistema desktop para análise automatizada de resultados de PCR em tempo real (qPCR/RT-qPCR), com foco em:
- Detecção automática de equipamentos (QuantStudio)
- Validação de regras analíticas (controles, CTs, outliers)
- Gestão de alertas e notificações
- Exportação multi-formato (PDF, Excel, CSV)
- Integração com sistema GAL (Ministério da Saúde)

### Stack Tecnológico

```
┌─────────────────────────────────────────────┐
│           Python 3.13                       │
├─────────────────────────────────────────────┤
│  Interface:      CustomTkinter 5.2.2        │
│  Data Analysis:  Pandas 2.1.4               │
│  Visualization:  Matplotlib 3.8.2           │
│  PDF Export:     ReportLab 4.0.7            │
│  Excel Export:   OpenPyXL 3.1.2             │
│  HTTP Client:    Requests 2.31.0            │
│  Persistence:    Pickle + CSV               │
│  Testing:        Pytest 7.4.3               │
└─────────────────────────────────────────────┘
```

### Requisitos do Sistema

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| **OS** | Windows 10 | Windows 11 |
| **Python** | 3.10 | 3.13 |
| **RAM** | 4 GB | 8 GB |
| **CPU** | Dual-core | Quad-core |
| **Disco** | 500 MB | 2 GB (com dados) |
| **Resolução** | 1280x720 | 1920x1080 |

---

## Arquitetura de Alto Nível

### Diagrama de Camadas

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                    │
│  ┌────────────────────────────────────────────────────┐ │
│  │  CustomTkinter UI (interface/)                    │ │
│  │  - Dashboard                                        │ │
│  │  - Extraction Views                                 │ │
│  │  - Analysis Views                                   │ │
│  │  - Configuration Screens                            │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Extraction  │  │   Analysis   │  │    Export    │  │
│  │  (extracao/) │  │  (analise/)  │  │(exportacao/) │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │    Alerts    │  │     GAL      │  │     Auth     │  │
│  │   (system)   │  │(exportacao/) │  │(autenticacao)│  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   INFRASTRUCTURE LAYER                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Persistence  │  │ Config Mgmt  │  │Error Handler │  │
│  │   (utils/)   │  │  (config/)   │  │   (utils/)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Database   │  │   Logging    │  │  Validation  │  │
│  │    (db/)     │  │   (logs/)    │  │   (utils/)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      DATA LAYER                          │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────┐   │
│  │ CSV Files  │  │Pickle Cache│  │  JSON Config    │   │
│  │  (banco/)  │  │  (data/)   │  │   (config/)     │   │
│  └────────────┘  └────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Princípios Arquiteturais

1. **Separação de Responsabilidades**: Camadas bem definidas
2. **Baixo Acoplamento**: Módulos independentes
3. **Alta Coesão**: Funcionalidades relacionadas agrupadas
4. **Injeção de Dependências**: Configuração externa
5. **Observer Pattern**: Sistema de eventos/alertas
6. **Singleton Pattern**: Gerenciadores únicos (Config, Persistence)

---

## Módulos e Componentes

### 1. Camada de Apresentação (`interface/`)

#### `dashboard.py`
- **Responsabilidade**: Tela principal do sistema
- **Componentes**:
  - `RecentAnalysisPanel`: Lista últimas 5 análises
  - `StatisticsPanel`: Cards com métricas (total análises, média CT, etc.)
  - `ActiveAlertsPanel`: Alertas não resolvidos (limitado a 10)
  - `QuickActionsPanel`: Botões de ação rápida
- **Atualização**: Automática a cada 30s (configurável)

#### `tela_extracao.py`
- **Responsabilidade**: Importação e validação de dados
- **Fluxo**:
  1. Seleção de arquivo (FileDialog)
  2. Detecção automática de equipamento
  3. Preview dos dados (TreeView)
  4. Validação de colunas obrigatórias
  5. Confirmação e persistência

#### `tela_analise.py`
- **Responsabilidade**: Visualização e edição de resultados
- **Features**:
  - Filtros dinâmicos (por resultado, CT, placa)
  - Edição inline (duplo clique)
  - Aplicação de regras manuais
  - Geração de gráficos sob demanda

#### `tela_configuracoes.py` (Fase 4.4)
- **Responsabilidade**: Gerenciamento de configurações
- **Arquitetura**:
  - Notebook com tabs (CTkTabview)
  - 11 categorias de configuração
  - Validação em tempo real
  - Export/Import JSON
  - Reset individual por categoria

### 2. Camada de Negócios

#### `extracao/busca_extracao.py`
- **Responsabilidade**: Detecção e parsing de equipamentos
- **Arquitetura**:
  ```python
  class EquipmentDetector:
      def detect(self, file_path: str) -> Equipment | None
      def parse(self, df: pd.DataFrame, equipment: Equipment) -> ParsedData
  
  # Suporta estratégia de detecção extensível:
  detectors = [
      QuantStudio3Detector(),
      QuantStudio5Detector(),
      QuantStudio7Detector(),
      # Fácil adicionar novos equipamentos
  ]
  ```

#### `analise/relatorios_qualidade_gerenciais.py`
- **Responsabilidade**: Aplicação de regras de validação
- **Regras Implementadas**:
  1. **Validação de CT**: `CT_MIN < CT < CT_MAX`
  2. **Controles Positivos**: `CT < 30` (configurável)
  3. **Controles Negativos**: `CT == "Undetermined"`
  4. **Detecção de Outliers**: Método IQR
  5. **Cross-validation**: Coerência entre alvos
  
- **Arquitetura**:
  ```python
  class RuleEngine:
      rules: List[Rule]
      
      def apply_rules(self, data: pd.DataFrame) -> ValidationResult:
          results = []
          for rule in self.rules:
              results.append(rule.validate(data))
          return aggregate_results(results)
  ```

#### Sistema de Alertas
- **Responsabilidade**: Monitoramento e notificação
- **Tipos de Alertas** (Enum):
  ```python
  class AlertType(Enum):
      CT_ALTO = "ct_alto"
      CT_BAIXO = "ct_baixo"
      PLACA_NAO_MAPEADA = "placa_nao_mapeada"
      AMOSTRA_INVALIDA = "amostra_invalida"
      ERRO_EXTRACAO = "erro_extracao"
      AVISO_QUALIDADE = "aviso_qualidade"
      INFO_SISTEMA = "info_sistema"
      SUCESSO = "sucesso"
      ERRO_CRITICO = "erro_critico"
  ```

- **Gerenciamento**:
  ```python
  class AlertManager(Observable):
      _instance = None  # Singleton
      
      def create_alert(self, tipo: AlertType, mensagem: str, 
                      severidade: int, dados: dict) -> Alert
      def mark_as_read(self, alert_id: str) -> None
      def resolve_alert(self, alert_id: str, obs: str) -> None
      def get_active_alerts(self) -> List[Alert]
      def notify_observers(self) -> None  # Observer Pattern
  ```

#### `exportacao/exportar_resultados.py`
- **Responsabilidade**: Geração de relatórios
- **Formatos**:
  1. **PDF** (ReportLab):
     - Template profissional
     - Gráficos embarcados
     - Logo institucional
     - Tabelas formatadas
  
  2. **Excel** (OpenPyXL):
     - Múltiplas abas (Resultados, Estatísticas, Alertas)
     - Formatação condicional (cores por resultado)
     - Gráficos nativos do Excel
  
  3. **CSV**:
     - Máxima compatibilidade
     - Encoding UTF-8 BOM

- **Otimizações**:
  - Cache de templates
  - Geração assíncrona (thread separada)
  - Compressão de imagens

#### `exportacao/envio_gal.py`
- **Responsabilidade**: Integração com API GAL
- **Protocolo**: REST API sobre HTTPS
- **Autenticação**: OAuth 2.0 + JWT tokens
- **Arquitetura**:
  ```python
  class GALClient:
      def __init__(self, base_url: str, credentials: Credentials):
          self.session = requests.Session()
          self.session.headers.update(self._get_auth_headers())
      
      def send_results(self, results: List[Result]) -> SendResult:
          # Validação local antes de envio
          validated = self.validate_locally(results)
          
          # Envio em lote (max 100 amostras por request)
          batches = chunk_list(validated, 100)
          responses = []
          
          for batch in batches:
              response = self._send_batch(batch)
              responses.append(response)
              
          return aggregate_responses(responses)
      
      def _send_batch(self, batch: List[Result]) -> Response:
          # Retry logic (3 tentativas, backoff exponencial)
          for attempt in range(3):
              try:
                  resp = self.session.post("/api/v2/results", 
                                           json=self._format_batch(batch),
                                           timeout=60)
                  resp.raise_for_status()
                  return resp.json()
              except requests.Timeout:
                  time.sleep(2 ** attempt)  # 1s, 2s, 4s
              except requests.HTTPError as e:
                  if e.response.status_code == 401:
                      self._refresh_token()
                  else:
                      raise
  ```

### 3. Camada de Infraestrutura

#### `config/settings.py` (Fase 4.4)
- **Responsabilidade**: Gerenciamento centralizado de configurações
- **Padrões**: Singleton + Observer
- **Estrutura**:
  ```python
  class ConfigurationManager(Observable):
      _instance = None
      _config: Dict[str, Any]
      _observers: List[ConfigObserver]
      
      def __new__(cls):
          if cls._instance is None:
              cls._instance = super().__new__(cls)
          return cls._instance
      
      def get(self, key: str, default: Any = None) -> Any:
          return self._config.get(key, default)
      
      def set(self, key: str, value: Any) -> None:
          old_value = self._config.get(key)
          self._config[key] = value
          self._notify_change(key, old_value, value)
      
      def salvar(self) -> None:
          # Backup automático antes de salvar
          self._create_backup()
          with open(CONFIG_FILE, 'w') as f:
              json.dump(self._config, f, indent=2)
      
      def exportar(self, path: str) -> None:
          shutil.copy(CONFIG_FILE, path)
      
      def importar(self, path: str) -> None:
          # Validação de schema antes de importar
          if self._validate_schema(path):
              shutil.copy(path, CONFIG_FILE)
              self._reload()
  ```

#### `utils/persistence.py` (Fase 4.4)
- **Responsabilidade**: Gerenciamento de estado e cache
- **Componentes**:
  1. **SessionManager**: Estado da aplicação
     ```python
     class SessionManager:
         def save_window_state(self, geometry: str, maximized: bool)
         def restore_window_state(self) -> WindowState
         def save_last_directory(self, dir_path: str)
         def get_last_directory(self) -> str
     ```
  
  2. **CacheManager**: Cache em memória + disco
     ```python
     class CacheManager:
         def __init__(self, max_size: int = 100, ttl: int = 3600):
             self._cache: Dict[str, CacheEntry] = {}
             self._max_size = max_size
             self._ttl = ttl  # Time-to-live em segundos
         
         def get(self, key: str) -> Any | None:
             entry = self._cache.get(key)
             if entry and not entry.is_expired():
                 return entry.value
             return None
         
         def set(self, key: str, value: Any, ttl: int = None) -> None:
             if len(self._cache) >= self._max_size:
                 self._evict_oldest()  # LRU eviction
             
             self._cache[key] = CacheEntry(
                 value=value,
                 timestamp=time.time(),
                 ttl=ttl or self._ttl
             )
     ```
  
  3. **HistoryManager**: Histórico de análises
     ```python
     class HistoryManager:
         def add_analysis(self, analysis: Analysis) -> None
         def get_recent(self, limit: int = 10) -> List[Analysis]
         def search(self, filters: dict) -> List[Analysis]
         def cleanup_old(self, days: int = 90) -> int
     ```

#### `utils/error_handler.py` (Fase 4.3)
- **Responsabilidade**: Tratamento centralizado de erros
- **Padrões**: Decorator + Logging
- **Implementação**:
  ```python
  class ErrorHandler:
      ERROR_TYPES = {
          FileNotFoundError: ErrorLevel.ERROR,
          PermissionError: ErrorLevel.CRITICAL,
          pd.errors.EmptyDataError: ErrorLevel.WARNING,
          requests.Timeout: ErrorLevel.WARNING,
          ValidationError: ErrorLevel.ERROR,
      }
      
      @staticmethod
      def safe_operation(func):
          """Decorator para operações que podem falhar"""
          @wraps(func)
          def wrapper(*args, **kwargs):
              try:
                  return func(*args, **kwargs)
              except Exception as e:
                  ErrorHandler.handle_error(e, context={
                      'function': func.__name__,
                      'args': args[:2],  # Primeiros 2 args (segurança)
                  })
                  return None
          return wrapper
      
      @staticmethod
      def handle_error(error: Exception, context: dict = None):
          # Log detalhado
          logger.error(f"Erro: {type(error).__name__}: {str(error)}", 
                      extra=context)
          
          # Criar alerta se apropriado
          if ErrorHandler._should_alert(error):
              alert_manager.create_alert(
                  tipo=AlertType.ERRO_CRITICO,
                  mensagem=ErrorHandler._user_friendly_message(error),
                  severidade=ErrorHandler._get_severity(error),
                  dados=context
              )
          
          # Tentativa de recuperação
          ErrorHandler._attempt_recovery(error, context)
  ```

#### `utils/validator.py` (Fase 4.3)
- **Responsabilidade**: Validações de dados
- **Métodos**:
  ```python
  class Validator:
      @staticmethod
      def validate_ct(ct_value: float) -> bool:
          """CT entre 0 e 50"""
          return 0 <= ct_value <= 50
      
      @staticmethod
      def validate_plate_format(plate_id: str) -> bool:
          """Formato: PLACA_YYYY_NNN"""
          pattern = r'^PLACA_\d{4}_\d{3}$'
          return bool(re.match(pattern, plate_id))
      
      @staticmethod
      def validate_sample_id(sample_id: str) -> bool:
          """Não vazio, alfanumérico, max 50 chars"""
          return bool(sample_id) and sample_id.isalnum() and len(sample_id) <= 50
      
      @staticmethod
      def validate_dataframe(df: pd.DataFrame, required_cols: List[str]) -> ValidationResult:
          """Valida estrutura de DataFrame"""
          missing = set(required_cols) - set(df.columns)
          if missing:
              return ValidationResult(
                  valid=False,
                  errors=[f"Colunas faltando: {', '.join(missing)}"]
              )
          
          # Verifica tipos de dados
          for col, expected_type in COLUMN_TYPES.items():
              if col in df.columns:
                  if not df[col].dtype == expected_type:
                      return ValidationResult(
                          valid=False,
                          errors=[f"Tipo incorreto em '{col}': esperado {expected_type}"]
                      )
          
          return ValidationResult(valid=True, errors=[])
  ```

#### `db/db_utils.py`
- **Responsabilidade**: Acesso a banco CSV
- **Tabelas**:
  - `usuarios.csv`: Credenciais (hasheadas)
  - `equipamentos.csv`: Equipamentos cadastrados
  - `placas.csv`: Mapeamento de placas
  - `exames_config.csv`: Configuração de protocolos
  - `regras.csv`: Regras customizadas
  - `sessoes.csv`: Sessões ativas
  - `configuracoes_sistema.csv`: Configs globais

- **CRUD Operations**:
  ```python
  class DatabaseManager:
      BASE_DIR = "banco/"
      
      @staticmethod
      def read_table(table_name: str) -> pd.DataFrame:
          path = os.path.join(DatabaseManager.BASE_DIR, f"{table_name}.csv")
          return pd.read_csv(path, encoding='utf-8-sig')
      
      @staticmethod
      def write_table(table_name: str, df: pd.DataFrame) -> None:
          path = os.path.join(DatabaseManager.BASE_DIR, f"{table_name}.csv")
          # Backup antes de escrever
          if os.path.exists(path):
              shutil.copy(path, f"{path}.bak")
          df.to_csv(path, index=False, encoding='utf-8-sig')
      
      @staticmethod
      def query(table_name: str, filters: dict) -> pd.DataFrame:
          df = DatabaseManager.read_table(table_name)
          for col, value in filters.items():
              df = df[df[col] == value]
          return df
  ```

---

## Fluxo de Dados

### Fluxo Completo de Análise

```
┌─────────────────┐
│  1. USUÁRIO     │
│  Seleciona      │
│  arquivo Excel  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  2. EXTRAÇÃO (extracao/busca_extracao)  │
│  ┌─────────────────────────────────┐   │
│  │ a) Ler arquivo (pandas)         │   │
│  │ b) Detectar equipamento          │   │
│  │ c) Validar estrutura             │   │
│  │ d) Parsear dados                 │   │
│  └─────────────────────────────────┘   │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  3. VALIDAÇÃO (utils/validator)         │
│  ┌─────────────────────────────────┐   │
│  │ - CTs válidos?                   │   │
│  │ - Colunas obrigatórias presentes?│   │
│  │ - IDs de amostra únicos?         │   │
│  └─────────────────────────────────┘   │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  4. ANÁLISE (analise/relatorios_...)    │
│  ┌─────────────────────────────────┐   │
│  │ RuleEngine aplica regras:        │   │
│  │ - Validação de controles         │   │
│  │ - Limites de CT                  │   │
│  │ - Detecção de outliers           │   │
│  │ - Cross-validation               │   │
│  └─────────────────────────────────┘   │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  5. ALERTAS (Sistema de Alertas)        │
│  ┌─────────────────────────────────┐   │
│  │ Se problemas detectados:         │   │
│  │ - Criar alertas                  │   │
│  │ - Notificar observers            │   │
│  │ - Atualizar badge no dashboard   │   │
│  └─────────────────────────────────┘   │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  6. VISUALIZAÇÃO (interface/tela_...)   │
│  ┌─────────────────────────────────┐   │
│  │ - Mostrar resultados em TreeView │   │
│  │ - Gerar gráficos (matplotlib)    │   │
│  │ - Aplicar filtros                │   │
│  │ - Permitir edição                │   │
│  └─────────────────────────────────┘   │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  7. EXPORTAÇÃO (exportacao/exportar_...) │
│  ┌─────────────────────────────────┐   │
│  │ Usuário escolhe formato:         │   │
│  │ - PDF → ReportLab                │   │
│  │ - Excel → OpenPyXL               │   │
│  │ - CSV → Pandas                   │   │
│  └─────────────────────────────────┘   │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  8. GAL (exportacao/envio_gal)          │
│  ┌─────────────────────────────────┐   │
│  │ - Autenticar via OAuth           │   │
│  │ - Formatar dados (JSON)          │   │
│  │ - Enviar via API REST            │   │
│  │ - Registrar protocolo            │   │
│  └─────────────────────────────────┘   │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  9. HISTÓRICO (utils/persistence)       │
│  ┌─────────────────────────────────┐   │
│  │ - Salvar em banco/logs           │   │
│  │ - Atualizar dashboard            │   │
│  │ - Limpar cache se necessário     │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Fluxo de Configurações (Fase 4.4)

```
┌──────────────┐
│   Usuário    │
│ abre Config  │
└──────┬───────┘
       │
       ▼
┌────────────────────────────────┐
│  ConfigurationManager          │
│  carrega config.json           │
└──────┬─────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│  Interface exibe valores       │
│  (tela_configuracoes.py)       │
└──────┬─────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│  Usuário altera valor          │
└──────┬─────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│  Validação em tempo real       │
│  (Validator)                   │
└──────┬─────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│  ConfigManager.set(key, val)   │
│  notifica observers            │
└──────┬─────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│  Componentes atualizam         │
│  (ex: Dashboard recarrega)     │
└──────┬─────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│  ConfigManager.salvar()        │
│  persiste em disco             │
└────────────────────────────────┘
```

---

## Camada de Persistência

### Estratégia Híbrida

1. **CSV** (Dados estruturados)
   - Vantagens: Legível, editável manualmente, versionável
   - Uso: Cadastros, configurações, mapeamentos
   - Encoding: UTF-8 BOM

2. **Pickle** (Cache de objetos)
   - Vantagens: Rápido, preserva tipos Python
   - Uso: Cache de DataFrames, sessões temporárias
   - Localização: `data/state/cache/`

3. **JSON** (Configurações)
   - Vantagens: Portável, legível, facilmente editável
   - Uso: `config.json`, templates de export
   - Validação: JSON Schema

### Backup Automático

```python
# Em config/settings.py
def salvar(self) -> None:
    # Backup antes de salvar
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"config/config_backup_{timestamp}.json"
    shutil.copy(CONFIG_FILE, backup_path)
    
    # Manter apenas últimos 5 backups
    backups = sorted(glob("config/config_backup_*.json"))
    for old_backup in backups[:-5]:
        os.remove(old_backup)
    
    # Salvar nova configuração
    with open(CONFIG_FILE, 'w') as f:
        json.dump(self._config, f, indent=2)
```

---

## Design Patterns Utilizados

### 1. Singleton

**Uso**: `ConfigurationManager`, `AlertManager`, `PersistenceManager`

**Justificativa**: Garantir instância única e estado global consistente.

```python
class ConfigurationManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = {}
        return cls._instance
```

### 2. Observer

**Uso**: Sistema de Alertas, Configurações

**Justificativa**: Desacoplar componentes que reagem a mudanças.

```python
class Observable:
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)
    
    def notify(self, event: Event) -> None:
        for observer in self._observers:
            observer.update(event)

class Dashboard(Observer):
    def update(self, event: Event) -> None:
        if event.type == "new_alert":
            self.refresh_alert_badge()
```

### 3. Strategy

**Uso**: Detecção de Equipamentos, Exportação

**Justificativa**: Algoritmos intercambiáveis sem modificar cliente.

```python
class ExportStrategy(ABC):
    @abstractmethod
    def export(self, data: pd.DataFrame, path: str) -> None:
        pass

class PDFExporter(ExportStrategy):
    def export(self, data, path):
        # Implementação com ReportLab
        pass

class ExcelExporter(ExportStrategy):
    def export(self, data, path):
        # Implementação com OpenPyXL
        pass

# Cliente
exporter = get_exporter(format)  # Retorna estratégia apropriada
exporter.export(data, output_path)
```

### 4. Decorator

**Uso**: Error Handling, Logging

**Justificativa**: Adicionar funcionalidades sem modificar código original.

```python
@safe_operation
@log_execution_time
def processar_placa(file_path: str) -> pd.DataFrame:
    # Lógica de processamento
    pass

# Equivalente a:
# processar_placa = log_execution_time(safe_operation(processar_placa))
```

### 5. Factory

**Uso**: Criação de Alertas, Validators

**Justificativa**: Encapsular lógica de criação de objetos complexos.

```python
class AlertFactory:
    @staticmethod
    def create_ct_alert(ct_value: float, limit: float, sample_id: str) -> Alert:
        if ct_value > limit:
            return Alert(
                tipo=AlertType.CT_ALTO,
                mensagem=f"CT {ct_value} acima do limite ({limit})",
                severidade=2,
                dados={'sample_id': sample_id, 'ct': ct_value}
            )
        else:
            return Alert(
                tipo=AlertType.CT_BAIXO,
                mensagem=f"CT {ct_value} abaixo do esperado",
                severidade=1,
                dados={'sample_id': sample_id, 'ct': ct_value}
            )
```

---

## Extensibilidade

### Adicionar Novo Equipamento

1. Crie detector em `extracao/`:
```python
# extracao/detectores/quantstudio_12.py
class QuantStudio12Detector(EquipmentDetector):
    def detect(self, df: pd.DataFrame) -> bool:
        # Lógica de detecção específica
        return "QuantStudio 12" in str(df.iloc[0, 0])
    
    def parse(self, df: pd.DataFrame) -> ParsedData:
        # Extração de colunas específicas
        return ParsedData(
            equipment="QuantStudio 12",
            samples=df['Sample Name'],
            cts=df['CT'],
            targets=df['Target Name'],
            # ...
        )
```

2. Registre em `banco/equipamentos.csv`:
```csv
id,nome,fabricante,detector_class
4,QuantStudio 12,Applied Biosystems,QuantStudio12Detector
```

3. O sistema detectará automaticamente.

### Adicionar Nova Regra de Validação

```python
# analise/regras/regra_customizada.py
class RegraVariacaoEntreDuplicatas(ValidationRule):
    def __init__(self, max_delta: float = 1.0):
        self.max_delta = max_delta
    
    def validate(self, data: pd.DataFrame) -> ValidationResult:
        # Agrupar por amostra
        grouped = data.groupby('Sample')['CT']
        
        alertas = []
        for sample, cts in grouped:
            if len(cts) >= 2:
                delta = cts.max() - cts.min()
                if delta > self.max_delta:
                    alertas.append(Alert(
                        tipo=AlertType.AVISO_QUALIDADE,
                        mensagem=f"Variação {delta:.2f} entre duplicatas de {sample}",
                        severidade=2
                    ))
        
        return ValidationResult(
            valid=len(alertas) == 0,
            alerts=alertas
        )

# Registrar regra
rule_engine.add_rule(RegraVariacaoEntreDuplicatas(max_delta=1.5))
```

### Adicionar Novo Formato de Exportação

```python
# exportacao/formats/markdown_exporter.py
class MarkdownExporter(ExportStrategy):
    def export(self, data: pd.DataFrame, path: str) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"# Relatório de Análise\n\n")
            f.write(f"**Data**: {datetime.now()}\n\n")
            f.write("## Resultados\n\n")
            f.write(data.to_markdown())

# Registrar em exportacao/exportar_resultados.py
EXPORTERS = {
    'pdf': PDFExporter(),
    'excel': ExcelExporter(),
    'csv': CSVExporter(),
    'markdown': MarkdownExporter(),  # Novo
}
```

---

## Performance e Otimização

### Benchmarks (Fase 4.2)

| Operação | Tempo Médio | Limite Aceitável |
|----------|-------------|------------------|
| Carregar dashboard | 459 ms | < 500 ms |
| Criar alerta | 0.08 ms | < 1 ms |
| Filtrar 1000 amostras | 0.04 ms | < 10 ms |
| Exportar PDF (100 amostras) | 2.3 s | < 5 s |
| Enviar para GAL (50 amostras) | 4.1 s | < 10 s |

### Otimizações Implementadas

1. **Cache de DataFrames**: Evita reprocessamento
   ```python
   @lru_cache(maxsize=10)
   def load_analysis(analysis_id: str) -> pd.DataFrame:
       return pd.read_pickle(f"data/analyses/{analysis_id}.pkl")
   ```

2. **Lazy Loading**: Dashboard carrega apenas visível
   ```python
   # Carrega apenas 5 análises recentes, não todas
   recent = history_manager.get_recent(limit=5)
   ```

3. **Indexação de DataFrames**: Acesso O(1)
   ```python
   df.set_index('Sample', inplace=True)
   sample_data = df.loc['AMOSTRA_001']  # Muito mais rápido
   ```

4. **Thread para Exportação**: UI não trava
   ```python
   def export_async(data, format, path):
       thread = Thread(target=exporter.export, args=(data, path))
       thread.start()
       # UI continua responsiva
   ```

5. **Compressão de Cache**: Economiza espaço
   ```python
   df.to_pickle(path, compression='gzip')
   ```

---

## Segurança

### Autenticação

- **Hash de Senhas**: SHA-256 com salt
  ```python
  def hash_password(password: str, salt: bytes = None) -> tuple:
      if salt is None:
          salt = os.urandom(32)
      pwd_hash = hashlib.sha256(salt + password.encode()).hexdigest()
      return pwd_hash, salt
  ```

- **Sessões**: Token UUID com expiração (configur ável)
  ```python
  session_token = str(uuid.uuid4())
  sessions[session_token] = {
      'user_id': user_id,
      'expires_at': datetime.now() + timedelta(hours=8)
  }
  ```

### Comunicação com GAL

- **HTTPS Only**: Criptografia TLS 1.2+
- **OAuth 2.0**: Tokens com refresh automático
- **Rate Limiting**: Max 10 requisições/minuto (client-side)

### Dados Sensíveis

- Senhas nunca em logs
- Dados de pacientes não persistidos (apenas resultados)
- Configuração pode excluir informações pessoais de exports

---

## Testes

### Pirâmide de Testes

```
        ┌──────────────┐
        │  E2E Tests   │  Fase 4.1 (9 testes)
        │   (1%)       │
        └──────────────┘
       ┌────────────────┐
       │ Integration    │  Fase 4.1 (9 testes)
       │ Tests (19%)    │
       └────────────────┘
      ┌──────────────────┐
      │  Unit Tests      │  Fase 2 (95 testes)
      │    (80%)         │
      └──────────────────┘
```

### Coverage (Fase 2)

- **Global**: 69%
- **Core Logic** (analise/, extracao/): 85%
- **Interface** (interface/): 45% (UI difícil de testar)

### Testes de Performance (Fase 4.2)

```python
# tests/test_performance.py
def test_dashboard_load_time():
    start = time.time()
    dashboard = Dashboard()
    dashboard.load_data()
    elapsed = time.time() - start
    assert elapsed < 0.5, f"Dashboard lento: {elapsed:.3f}s"

def test_alert_creation_speed():
    start = time.time()
    for _ in range(1000):
        alert_manager.create_alert(AlertType.INFO_SISTEMA, "Teste", 1, {})
    elapsed = time.time() - start
    assert elapsed < 0.1, f"Criação de alertas lenta: {elapsed:.3f}s"
```

### Testes de Memória (Fase 4.2)

```python
# tests/test_memory.py
def test_memory_leak_with_10k_alerts():
    import tracemalloc
    tracemalloc.start()
    
    for i in range(10000):
        alert_manager.create_alert(AlertType.INFO_SISTEMA, f"Alerta {i}", 1, {})
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Deve consumir < 50 MB para 10k alertas
    assert peak < 50 * 1024 * 1024, f"Vazamento de memória: {peak / 1024 / 1024:.1f} MB"
```

---

## Roadmap Técnico

### v1.1 (Q1 2026)

- [ ] **API REST**: Integração externa
- [ ] **Processamento em Lote**: Múltiplas placas
- [ ] **Suporte a PostgreSQL**: Alternativa ao CSV
- [ ] **Dashboard Web** (Flask/FastAPI)

### v1.2 (Q2 2026)

- [ ] **Multilíngue**: Inglês, Espanhol
- [ ] **Permissões Granulares**: RBAC completo
- [ ] **Integração com LIMS**: Bidirectional sync
- [ ] **Relatórios Customizáveis**: Drag-and-drop builder

### v1.3 (Q3 2026)

- [ ] **Machine Learning**: Predição de falhas
- [ ] **Mobile App**: Visualização/aprovação
- [ ] **Cloud Storage**: Backup automático (Azure/AWS)
- [ ] **Colaboração**: Comentários, aprovações em equipe

---

## 📚 Referências

- **CustomTkinter Docs**: https://github.com/TomSchimansky/CustomTkinter
- **Pandas API**: https://pandas.pydata.org/docs/
- **ReportLab User Guide**: https://www.reportlab.com/docs/reportlab-userguide.pdf
- **Pytest Documentation**: https://docs.pytest.org/

---

## 🤝 Contribuindo

### Setup de Desenvolvimento

```powershell
# Clone e instale em modo de desenvolvimento
git clone https://github.com/Marciopachecolab/IntegRAGal.git
cd IntegRAGal
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Ferramentas de dev

# Execute testes
pytest tests/ -v --cov

# Lint
flake8 --max-line-length=100 *.py */**.py
black .  # Formatação automática

# Type checking
mypy main.py
```

### Convenções de Código

- **PEP 8**: Seguir guia de estilo Python
- **Type Hints**: Obrigatório em funções públicas
- **Docstrings**: Google Style
- **Commits**: Conventional Commits (feat:, fix:, docs:)

Exemplo:
```python
def processar_amostra(sample_id: str, ct_value: float) -> ValidationResult:
    """
    Processa uma amostra individual aplicando regras de validação.
    
    Args:
        sample_id: Identificador único da amostra
        ct_value: Valor de CT (Cycle Threshold)
    
    Returns:
        ValidationResult contendo status e alertas gerados
    
    Raises:
        ValueError: Se ct_value for negativo ou > 50
    
    Example:
        >>> processar_amostra("AMOSTRA_001", 28.5)
        ValidationResult(valid=True, alerts=[])
    """
    pass
```

---

**Atualizado**: Dezembro 2025  
**Versão**: 1.0.0  
**Autor**: Márcio Pacheco  
**Contato**: marcio@integragal.com
