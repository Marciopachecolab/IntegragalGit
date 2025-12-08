# ⚡ Guia Rápido: Implementação do Histórico Multi-Exame

## 📋 Resumo da Solução

Sua situação:
- ✅ CSV com histórico funciona
- ❌ Mas só suporta VR1e2
- ❌ Precisa suportar VR1, VR2, ZDC, etc.
- ❌ Precisa rastrear envio para GAL

Solução:
- ✅ Adicionar UUID a cada registro (id_registro)
- ✅ Adicionar campos de rastreamento GAL
- ✅ Suportar múltiplos exames dinamicamente
- ✅ Atualizar CSV quando enviado para GAL

---

## 🚀 Implementação Rápida (5 Passos)

### PASSO 1: Executar Migração

```bash
# Navega para a pasta do projeto
cd c:\Users\marci\downloads\integragal

# Executa script de migração
python scripts/migrate_historical_csv.py

# Resultado: 
# - Backup criado (historico_analises_backup_20251207_143022.csv)
# - UUIDs gerados para todos os registros
# - 4 novos campos adicionados
# - CSV validado
```

**O que muda no CSV:**

```
ANTES:
data_hora_analise;usuario_analise;exame;...;status_gal;mensagem_gal;criado_em;atualizado_em

DEPOIS:
id_registro;data_hora_analise;usuario_analise;exame;...;status_gal;mensagem_gal;data_hora_envio;usuario_envio;sucesso_envio;detalhes_envio;criado_em;atualizado_em
   ↑                                                                      ↑                    ↑              ↑               ↑
  NOVO                                                                 NOVOS CAMPOS DE RASTREAMENTO
```

---

### PASSO 2: Atualizar `gerar_historico_csv()` em history_report.py

Substituir a função existente com esta versão que:
- Suporta QUALQUER exame
- Gera UUID automático
- Inicializa campos GAL

**Localização:** `services/history_report.py` (linhas 70-211)

```python
import uuid

def gerar_historico_csv(
    df_final: pd.DataFrame,
    exame: str,
    usuario: str,
    lote: str = "",
    arquivo_corrida: str = "",
    caminho_csv: str = "logs/historico_analises.csv",
) -> None:
    """Versão evoluída com UUID e suporte multi-exame"""
    
    cfg = get_exam_cfg(exame)
    
    if cfg is None:
        raise ValueError(f"Exame '{exame}' não encontrado no registry")
    
    # ... código anterior para descobrir alvos/CTs ...
    
    linhas = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for _, r in df_final.iterrows():
        # ✅ NOVO: Gera UUID
        id_registro = str(uuid.uuid4())
        
        codigo = str(r.get("Codigo", "")).strip()
        amostra = str(r.get("Amostra", "")).strip()
        poco = str(r.get("Poco", "")).strip()
        status_corrida = str(r.get("Status_Corrida", "")).strip()
        
        status_gal = "não enviado"  # ✅ NOVO: Default melhorado
        mensagem_gal = ""
        
        cod_lower = codigo.lower()
        if (not codigo.isdigit()) or ("cn" in cod_lower) or ("cp" in cod_lower):
            status_gal = "não enviável"
            mensagem_gal = "Código não numérico ou controle"
        
        # ✅ NOVA ESTRUTURA
        linha = {
            "id_registro": id_registro,              # NOVO
            "data_hora_analise": timestamp,
            "usuario_analise": usuario,
            "exame": exame,
            "lote": lote or "",
            "arquivo_corrida": arquivo_corrida or "",
            "poco": poco,
            "amostra": amostra,
            "codigo": codigo,
            "status_corrida": status_corrida,
            
            # ... SC2 - R, SC2 - CT, HMPV - R, etc. (conforme exame) ...
            
            "status_gal": status_gal,
            "mensagem_gal": mensagem_gal,
            "data_hora_envio": None,      # NOVO
            "usuario_envio": None,         # NOVO
            "sucesso_envio": None,         # NOVO
            "detalhes_envio": "",          # NOVO
            "criado_em": timestamp,
            "atualizado_em": timestamp,
        }
        
        # ... resto do processamento igual ...
        
        linhas.append(linha)
    
    # ... escreve CSV igual ...
```

---

### PASSO 3: Importar Módulo de Sincronização

**Onde usar:** Quando enviar para GAL, importe `history_gal_sync.py`

```python
# No arquivo exportacao/envio_gal.py ou onde faz o envio

from services.history_gal_sync import marcar_enviados, marcar_falha

# Após envio bem-sucedido
if sucesso:
    resultado = marcar_enviados(
        id_registros=lista_de_uuids,
        usuario="márcio",
        csv_path="logs/historico_analises.csv"
    )
    print(f"✅ {resultado['registros_atualizados']} registros marcados como enviados")

# Se falhar
else:
    resultado = marcar_falha(
        id_registros=lista_de_uuids,
        usuario="márcio",
        erro="Erro de conexão com servidor GAL",
        csv_path="logs/historico_analises.csv"
    )
    print(f"❌ {resultado['registros_atualizados']} registros marcados como falha")
```

---

### PASSO 4: Testar com VR1e2 (Exame Existente)

```bash
# Abrir aplicação
python main.py

# 1. Fazer análise com VR1e2
# 2. Salvar no histórico
# 3. Verificar que:
#    - CSV foi adicionado
#    - id_registro tem UUID
#    - status_gal = "não enviado"
#    - data_hora_envio = NULL
```

---

### PASSO 5: Testar com ZDC (Novo Exame)

```bash
# 1. Fazer análise com ZDC (deve carregar config do registry)
# 2. Salvar no histórico
# 3. Verificar que:
#    - ZDC tem 6 alvos (DEN1, DEN2, DEN3, DEN4, ZYK, CHIK)
#    - VR1e2 continua com 7 alvos (SC2, HMPV, INF A, INF B, ADV, RSV, HRV)
#    - CSV mescla ambos automaticamente
```

---

## 🔍 Verificação Pós-Implementação

### Verificar se Migração Funcionou

```bash
# Abrir arquivo com PowerShell
$csv = "C:\Users\marci\downloads\integragal\logs\historico_analises.csv"
$df = Import-Csv $csv -Delimiter ";"

# Verificar colunas
$df[0].PSObject.Properties | Select-Object Name

# Esperado:
# id_registro, data_hora_analise, usuario_analise, exame, ..., 
# data_hora_envio, usuario_envio, sucesso_envio, detalhes_envio, ...
```

### Verificar se UUID é Único

```python
import pandas as pd

df = pd.read_csv("logs/historico_analises.csv", sep=";")

# Checar duplicados
duplicados = df["id_registro"].duplicated().sum()
print(f"UUIDs duplicados: {duplicados}")  # Deve ser 0

# Checar nulos
nulos = df["id_registro"].isna().sum()
print(f"UUIDs nulos: {nulos}")  # Deve ser 0
```

---

## 📊 Exemplo de Fluxo Completo

### Antes da Implementação (Hoje)

```
1. Análise VR1e2
   └─ Salva no CSV com status="analizado e nao enviado"
   └─ Sem UUID
   └─ Sem campo de envio GAL

2. Análise ZDC
   └─ PROBLEMA: Alvos diferentes (6 vs 7)
   └─ Não funciona com estrutura atual
```

### Depois da Implementação

```
1. Análise VR1e2
   └─ Salva com id_registro="550e8400-..."
   └─ status_gal="não enviado"
   └─ data_hora_envio=NULL
   └─ 7 alvos (SC2, HMPV, INF A, INF B, ADV, RSV, HRV)

2. Análise ZDC
   └─ Salva com id_registro="550e8401-..."
   └─ status_gal="não enviado"
   └─ data_hora_envio=NULL
   └─ 6 alvos (DEN1, DEN2, DEN3, DEN4, ZYK, CHIK)

3. CSV contém AMBOS, mesclados automaticamente
   ├─ VR1e2: 7 colunas de alvos
   ├─ ZDC: 6 colunas de alvos
   └─ Colunas extras têm NULL quando não usadas

4. Enviar para GAL
   └─ Sistema busca registros com status="não enviado"
   └─ Envia cada exame com seus alvos/CTs específicos
   └─ Após sucesso, atualiza:
      ├─ data_hora_envio="2025-12-05 20:15:00"
      ├─ usuario_envio="márcio"
      ├─ sucesso_envio=True
      └─ status_gal="enviado"
```

---

## ⚙️ Integração com Código Existente

### Onde Modificar

| Arquivo | Linha | Modificação |
|---------|-------|-------------|
| `services/history_report.py` | 70 | Adicionar `import uuid` |
| `services/history_report.py` | ~80 | Gerar UUID em cada linha |
| `services/history_report.py` | ~170 | Adicionar 4 novos campos |
| `exportacao/envio_gal.py` | ? | Importar `marcar_enviados` |
| `exportacao/envio_gal.py` | ? | Chamar `marcar_enviados` após sucesso |
| `utils/gui_utils.py` | ? | Opcional: mostrar UUID no histórico |

### Impacto em Código Existente

| Componente | Impacto |
|-----------|---------|
| `gerar_historico_csv()` | ✅ Backward compatible (novos parâmetros opcionais) |
| `_salvar_selecionados()` | ✅ Sem mudança (chama gerar_historico_csv normalmente) |
| CSV existente | ✅ Será migrado com backup automático |
| PostgreSQL | ✅ Sem mudança (continua optional) |
| Relatórios | ✅ Sem mudança (CSV continua com mesmos dados) |

---

## 🎯 Checklist Final

- [ ] **Passo 1:** Executar `migrate_historical_csv.py`
- [ ] **Passo 1:** Verificar backup foi criado
- [ ] **Passo 1:** Validar CSV tem 4 novos campos
- [ ] **Passo 2:** Atualizar `gerar_historico_csv()` com UUID
- [ ] **Passo 2:** Testar que análise VR1e2 salva com UUID
- [ ] **Passo 3:** Copiar `history_gal_sync.py` para services/
- [ ] **Passo 3:** Testar importação do módulo
- [ ] **Passo 4:** Fazer análise com ZDC
- [ ] **Passo 4:** Verificar que ZDC salva com 6 alvos
- [ ] **Passo 5:** Integrar `marcar_enviados()` no envio GAL
- [ ] **Passo 5:** Testar que status_gal atualiza após envio
- [ ] **Final:** Rodar FASE 7 E2E tests novamente

---

## 📞 Dúvidas Frequentes

**P: E se um exame tiver mais alvos no futuro?**
R: CSV adicionará colunas automaticamente. Migração não é necessária.

**P: E dados antigos (apenas VR1e2)?**
R: Continuam funcionando. Backup salvo. UUID gerado para todos.

**P: E se alguém tentar enviar sem migrar?**
R: `history_gal_sync.py` valida estrutura CSV e mostra erro claro.

**P: Posso voltar à versão antiga se der problema?**
R: Sim. Backup criado automaticamente em `historico_analises_backup_*.csv`

**P: CSV fica muito grande?**
R: Uma linha ≈ 1-2KB. 10k amostras = 10-20MB. Problema? Implementar sharding por data.

---

## 📚 Próximos Passos

1. ✅ Você implementa os 5 passos acima
2. ✅ Testa com VR1e2 e ZDC
3. ✅ Avisa quando quiser adicionar novo exame (VR1, VR2, etc.)
4. ✅ Sistema continua funcionando sem mudança estrutural

Quer que eu prepare qualquer detalhe adicional?
