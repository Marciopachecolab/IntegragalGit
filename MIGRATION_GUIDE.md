# Guia de Migração - IntegRAGal Refatorado

**Versão:** 1.0  
**Data:** 10 de dezembro de 2025  
**Branch:** `refactoring/eliminate-redundancies` → `master`

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Mudanças Críticas](#mudanças-críticas)
3. [Guia de Migração por Módulo](#guia-de-migração-por-módulo)
4. [Exemplos de Código](#exemplos-de-código)
5. [Solução de Problemas](#solução-de-problemas)
6. [FAQ](#faq)

---

## 📖 Visão Geral

Este guia ajuda desenvolvedores a migrar código existente para a nova arquitetura refatorada do IntegRAGal. 

### O que mudou?
- ✅ Eliminados circular imports
- ✅ Configuração unificada (ConfigService)
- ✅ CLI consolidado (main.py)
- ✅ Histórico consolidado (PostgreSQL como fonte)
- ✅ Formatação GAL em módulo dedicado

### O que NÃO mudou?
- ✅ API pública mantida com wrappers de compatibilidade
- ✅ Scripts run_*.py ainda funcionam (com warnings)
- ✅ Estrutura de banco de dados inalterada
- ✅ Formatos de arquivos CSV/Excel mantidos

---

## 🚨 Mudanças Críticas

### 1. Sistema de Configuração

#### ❌ DEPRECATED
```python
from config.settings import ConfigurationManager

config = ConfigurationManager()
valor = config.get("chave")
config.set("chave", "valor")
config.save()
```

#### ✅ RECOMENDADO
```python
from services.config_service import config_service

valor = config_service.get("chave")
config_service.set("chave", "valor")
config_service.save()
```

**Por quê?**
- ConfigService é a fonte única de verdade
- ConfigurationManager agora é apenas um adapter (deprecated)
- ConfigService lê/escreve em `config.json` (raiz)

**Timeline:**
- **Atual:** Ambos funcionam, ConfigurationManager emite warning
- **v2.0:** ConfigurationManager será removido

---

### 2. Formatação GAL

#### ❌ DEPRECATED
```python
from main import _formatar_para_gal

df_formatado = _formatar_para_gal(df, exame="vr1e2")
```

#### ✅ RECOMENDADO
```python
from exportacao.gal_formatter import formatar_para_gal

df_formatado = formatar_para_gal(df, exame="vr1e2")
```

**Por quê?**
- `_formatar_para_gal` foi movido de `main.py` para módulo dedicado
- Wrapper em `main.py` mantido apenas para compatibilidade
- Arquitetura mais limpa (separação de responsabilidades)

**Timeline:**
- **Atual:** Ambos funcionam, `main._formatar_para_gal` emite warning
- **v2.0:** Wrapper em `main.py` será removido

---

### 3. CLI e Entry Points

#### ❌ DEPRECATED
```bash
# Scripts individuais
python run_dashboard.py
python run_historico.py
python run_alertas.py
python run_graficos.py
python run_visualizador.py
```

#### ✅ RECOMENDADO
```bash
# CLI unificado
python main.py dashboard
python main.py historico
python main.py alertas
python main.py graficos
python main.py visualizador
```

**Por quê?**
- Reduz duplicação de código
- Interface consistente
- Facilita adição de novos comandos

**Timeline:**
- **Atual:** Scripts `run_*.py` funcionam com deprecation warning
- **v2.0:** Scripts `run_*.py` serão removidos

---

### 4. Histórico de Análises

#### ❌ DEPRECATED
```python
# Leitura do CSV antigo
import pandas as pd

df = pd.read_csv("reports/historico_analises.csv")
```

#### ✅ RECOMENDADO
```python
# Opção 1: Ler do CSV consolidado (view)
import pandas as pd

df = pd.read_csv(
    "logs/historico_analises.csv",
    sep=';',
    encoding='utf-8',
    low_memory=False
)

# Opção 2: Ler direto do PostgreSQL (fonte de verdade)
from db.db_utils import buscar_historico_processamento

df = buscar_historico_processamento()
```

**Por quê?**
- PostgreSQL é a fonte única de verdade
- CSV movido para `logs/` (antes em `reports/`)
- CSV requer encoding correto (UTF-8) e separador (;)

**Ação Necessária:**
- Atualizar caminhos: `reports/` → `logs/`
- Adicionar parâmetros corretos ao `pd.read_csv()`

---

### 5. Notificações GAL

#### ❌ DEPRECATED
```python
from main import _notificar_gal_saved

_notificar_gal_saved(lote="ABC123", quantidade=10)
```

#### ✅ RECOMENDADO
```python
from utils.notifications import notificar_gal_saved

notificar_gal_saved(lote="ABC123", quantidade=10)
```

**Por quê?**
- Função movida para módulo utilitário dedicado
- Elimina circular import com `main.py`

---

## 🔄 Guia de Migração por Módulo

### Interface Gráfica (CustomTkinter)

#### Tela de Configurações

**Antes:**
```python
from config.settings import ConfigurationManager

class TelaConfiguracoes:
    def __init__(self):
        self.config_manager = ConfigurationManager()
        valor = self.config_manager.get("gal_url")
```

**Depois:**
```python
from services.config_service import config_service

class TelaConfiguracoes:
    def __init__(self):
        # Usar diretamente config_service (singleton)
        valor = config_service.get("gal_url")
```

#### Dashboard

**Antes:**
```python
# Caminho antigo
df = pd.read_csv("reports/historico_analises.csv")
```

**Depois:**
```python
# Caminho novo + encoding correto
df = pd.read_csv(
    "logs/historico_analises.csv",
    sep=';',
    encoding='utf-8',
    low_memory=False
)
```

---

### Menu Handler

#### Exportação GAL

**Antes:**
```python
from main import _formatar_para_gal, _notificar_gal_saved

# Formatar dados
df_gal = _formatar_para_gal(df, exame="vr1e2")

# Notificar sucesso
_notificar_gal_saved(lote="ABC", quantidade=10)
```

**Depois:**
```python
from exportacao.gal_formatter import formatar_para_gal
from utils.notifications import notificar_gal_saved

# Formatar dados
df_gal = formatar_para_gal(df, exame="vr1e2")

# Notificar sucesso
notificar_gal_saved(lote="ABC", quantidade=10)
```

---

### Scripts e Automação

#### Scripts Run_*

**Antes:**
```python
# run_dashboard.py
from interface.dashboard import Dashboard

app = Dashboard()
app.mainloop()
```

**Depois (via CLI):**
```bash
# Linha de comando
python main.py dashboard
```

**Ou manter script com warning:**
```python
# run_dashboard.py (mantido para compatibilidade)
import warnings

warnings.warn(
    "run_dashboard.py está deprecated. Use: python main.py dashboard",
    DeprecationWarning,
    stacklevel=2
)

from interface.dashboard import Dashboard
app = Dashboard()
app.mainloop()
```

---

### Banco de Dados

#### Salvar Histórico

**Antes:**
```python
# Salvar direto no CSV
df.to_csv("reports/historico_analises.csv", index=False)
```

**Depois:**
```python
# Sempre salvar no PostgreSQL (fonte de verdade)
from db.db_utils import salvar_historico_processamento

salvar_historico_processamento(
    usuario="user",
    exame="COVID",
    status="OK",
    lote="ABC123"
)

# CSV será gerado automaticamente via script consolidate_history.py
```

---

## 💡 Exemplos de Código

### Exemplo 1: Aplicação Completa

**Antes (código antigo):**
```python
# app_antigo.py
from config.settings import ConfigurationManager
from main import _formatar_para_gal, _notificar_gal_saved
import pandas as pd

# Carregar config
config = ConfigurationManager()
gal_url = config.get("gal_url")

# Carregar dados
df = pd.read_csv("reports/historico_analises.csv")

# Formatar para GAL
df_gal = _formatar_para_gal(df, exame="vr1e2")

# Notificar
_notificar_gal_saved(lote="ABC", quantidade=len(df_gal))
```

**Depois (código migrado):**
```python
# app_novo.py
from services.config_service import config_service
from exportacao.gal_formatter import formatar_para_gal
from utils.notifications import notificar_gal_saved
import pandas as pd

# Carregar config (singleton, sem instanciar)
gal_url = config_service.get("gal_url")

# Carregar dados (novo caminho + encoding)
df = pd.read_csv(
    "logs/historico_analises.csv",
    sep=';',
    encoding='utf-8',
    low_memory=False
)

# Formatar para GAL
df_gal = formatar_para_gal(df, exame="vr1e2")

# Notificar
notificar_gal_saved(lote="ABC", quantidade=len(df_gal))
```

---

### Exemplo 2: Integração com GAL

**Antes:**
```python
# integracao_gal.py
from main import _formatar_para_gal
from exportacao.envio_gal import enviar_para_gal

df = processar_resultados()
df_formatado = _formatar_para_gal(df, exame="vr1e2")
enviar_para_gal(df_formatado)
```

**Depois:**
```python
# integracao_gal.py
from exportacao.gal_formatter import formatar_para_gal
from exportacao.envio_gal import enviar_para_gal

df = processar_resultados()
df_formatado = formatar_para_gal(df, exame="vr1e2")
enviar_para_gal(df_formatado)
```

---

### Exemplo 3: Leitura de Configuração

**Antes:**
```python
# Instanciar ConfigurationManager
from config.settings import ConfigurationManager

def carregar_credenciais():
    config = ConfigurationManager()
    usuario = config.get("gal_usuario")
    senha = config.get("gal_senha")
    return usuario, senha
```

**Depois:**
```python
# Usar singleton config_service
from services.config_service import config_service

def carregar_credenciais():
    # Sem instanciar, usar diretamente
    usuario = config_service.get("gal_usuario")
    senha = config_service.get("gal_senha")
    return usuario, senha
```

---

## 🔧 Solução de Problemas

### Problema 1: ImportError após migração

**Erro:**
```
ImportError: cannot import name '_formatar_para_gal' from 'main'
```

**Causa:**
- Código tentando importar função deprecated de `main.py`

**Solução:**
```python
# Substituir
from main import _formatar_para_gal

# Por
from exportacao.gal_formatter import formatar_para_gal
```

---

### Problema 2: CSV não encontrado

**Erro:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'reports/historico_analises.csv'
```

**Causa:**
- Caminho antigo (`reports/`) não existe mais

**Solução:**
```python
# Substituir
df = pd.read_csv("reports/historico_analises.csv")

# Por
df = pd.read_csv("logs/historico_analises.csv", sep=';', encoding='utf-8')
```

---

### Problema 3: Encoding incorreto no CSV

**Erro:**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte...
```

**Causa:**
- CSV requer encoding UTF-8 explícito

**Solução:**
```python
# Adicionar parâmetros corretos
df = pd.read_csv(
    "logs/historico_analises.csv",
    sep=';',              # Separador correto
    encoding='utf-8',     # Encoding explícito
    low_memory=False      # Evitar avisos de tipo
)
```

---

### Problema 4: ConfigurationManager emitindo warnings

**Warning:**
```
DeprecationWarning: ConfigurationManager está deprecated. 
Use services.config_service
```

**Causa:**
- Código usando ConfigurationManager (deprecated)

**Solução:**
```python
# Migrar de
from config.settings import ConfigurationManager
config = ConfigurationManager()

# Para
from services.config_service import config_service
# Usar diretamente, sem instanciar
```

---

### Problema 5: Scripts run_* emitindo warnings

**Warning:**
```
DeprecationWarning: run_dashboard.py está deprecated.
Use: python main.py dashboard
```

**Causa:**
- Usando scripts individuais em vez de CLI unificado

**Solução:**
```bash
# Substituir
python run_dashboard.py

# Por
python main.py dashboard
```

---

## ❓ FAQ

### Q1: Meu código antigo vai parar de funcionar?

**R:** Não imediatamente. Toda a refatoração mantém backward compatibility:
- Funções antigas têm wrappers que emitem warnings
- Scripts `run_*.py` ainda funcionam (com warnings)
- ConfigurationManager redireciona para ConfigService

**Timeline de remoção:** v2.0 (futuro)

---

### Q2: Preciso migrar tudo de uma vez?

**R:** Não. Você pode migrar gradualmente:
1. Comece com novos módulos (use a API nova)
2. Migre módulos críticos (config, GAL)
3. Atualize scripts de automação
4. Por último, migre código legado menos usado

---

### Q3: Como verifico se meu código usa APIs deprecated?

**R:** Execute com warnings habilitados:
```bash
python -W all::DeprecationWarning main.py
```

Você verá todos os warnings de deprecação.

---

### Q4: O que acontece se eu não migrar?

**R:** Atualmente:
- Código funciona normalmente
- Warnings aparecem no log

Versão v2.0 (futura):
- Wrappers deprecated serão removidos
- Código não migrado vai quebrar

**Recomendação:** Migre durante janela de manutenção para evitar problemas futuros.

---

### Q5: Como saber qual versão estou usando?

**R:**
```python
import main
print(main.__doc__)  # Mostra versão no docstring
```

Ou verificar tag do git:
```bash
git describe --tags
```

---

### Q6: Meus testes vão passar após migração?

**R:** Sim, desde que você:
1. Atualize imports deprecated
2. Corrija caminhos de CSV (reports/ → logs/)
3. Adicione encoding='utf-8' ao ler CSVs

Testes de referência (85+ passando):
```bash
python -m pytest tests/test_formula_parser.py -v
python -m pytest tests/test_equipment_registry.py -v
```

---

### Q7: Como reportar problemas?

**R:**
1. Verifique [REFACTORING_CHANGELOG.md](REFACTORING_CHANGELOG.md)
2. Consulte este guia
3. Verifique issues no repositório
4. Crie issue com:
   - Código antigo (antes)
   - Código tentado (depois)
   - Error trace completo

---

## 📚 Recursos Adicionais

### Documentação Relacionada
- [REFACTORING_CHANGELOG.md](REFACTORING_CHANGELOG.md) - Todas as mudanças
- [RELATORIO_REDUNDANCIA_CONFLITOS.md](RELATORIO_REDUNDANCIA_CONFLITOS.md) - Análise original
- [FASE3_CONCLUIDA.md](docs/FASE3_CONCLUIDA.md) - Detalhes da consolidação

### Arquivos de Referência
- `exportacao/gal_formatter.py` - Formatação GAL (nova)
- `services/config_service.py` - Config unificado
- `main.py` - CLI e wrappers de compatibilidade
- `db/db_utils.py` - Operações de banco (histórico)

### Scripts Úteis
```bash
# Gerar CSV atualizado do PostgreSQL
python scripts/consolidate_history.py

# Testar importações
python -c "from exportacao.gal_formatter import formatar_para_gal"

# Verificar warnings deprecated
python -W all::DeprecationWarning main.py --help
```

---

## ✅ Checklist de Migração

Use esta checklist para garantir migração completa:

### Configuração
- [ ] Substituído `ConfigurationManager` por `config_service`
- [ ] Removidas instâncias de `ConfigurationManager()`
- [ ] Testado `config_service.get()` e `.set()`

### Formatação GAL
- [ ] Substituído `main._formatar_para_gal` por `gal_formatter.formatar_para_gal`
- [ ] Importado de `exportacao.gal_formatter`
- [ ] Testado formatação com exames conhecidos

### Notificações
- [ ] Substituído `main._notificar_gal_saved` por `notifications.notificar_gal_saved`
- [ ] Importado de `utils.notifications`

### Histórico
- [ ] Atualizado caminhos de `reports/` para `logs/`
- [ ] Adicionado `sep=';'` ao `pd.read_csv()`
- [ ] Adicionado `encoding='utf-8'` ao `pd.read_csv()`
- [ ] Preferido PostgreSQL como fonte (quando possível)

### CLI e Scripts
- [ ] Migrado chamadas para `python main.py <comando>`
- [ ] Atualizado documentação interna
- [ ] Atualizado scripts de automação/deploy

### Testes
- [ ] Executado pytest com sucesso
- [ ] Verificado que não há warnings de importação
- [ ] Testado fluxo completo (ponta a ponta)

---

**Última atualização:** 10 de dezembro de 2025  
**Versão do guia:** 1.0  
**Branch:** refactoring/eliminate-redundancies
