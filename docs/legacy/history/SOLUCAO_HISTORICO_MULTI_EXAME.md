# 🎯 Solução Recomendada: Histórico Multi-Exame com Rastreamento de Envio GAL

## 📋 Problema

**Situação atual:**
- CSV histórico contém apenas dados do VR1e2 Biomanguinhos
- Precisa suportar múltiplos exames (VR1, VR2, VR1e2, ZDC, etc.)
- Cada exame tem seus próprios alvos e CTs
- Registros precisam rastrear: criação, envio para GAL, timestamp, usuário e sucesso

**Requisitos:**
1. ✅ Armazenar TODOS os exames com seus alvos e CTs específicos
2. ✅ Status inicial: "não enviado para GAL"
3. ✅ Atualizar após envio: timestamp, usuário, sucesso
4. ✅ Manter compatibilidade com CSV
5. ✅ Não quebrar dados existentes

---

## 🏗️ Arquitetura Recomendada

### Estrutura do CSV Evoluída

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CAMPOS DE IDENTIFICAÇÃO E RASTREABILIDADE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ id_registro        │ UUID único para cada linha                             │
│ data_hora_analise  │ Quando foi feita a análise (imutável)                 │
│ usuario_analise    │ Quem fez a análise (imutável)                         │
│ exame              │ Qual exame (VR1e2, ZDC, VR1, etc.)                    │
│ lote               │ ID do lote de análises                                 │
│ arquivo_corrida    │ Arquivo source da análise                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ DADOS DA AMOSTRA                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ poco               │ Posição na placa (A1+A2, G11+G12, etc.)               │
│ amostra            │ ID da amostra                                          │
│ codigo             │ Código (numérico ou controle)                          │
│ status_corrida     │ Status de processamento (Válida, Inválida, etc.)      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ RESULTADOS QUALITATIVOS (dinâmicos por exame)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ <ALVO> - R         │ Ex: SC2 - R, HMPV - R (código 1/2/3)                  │
│ <ALVO> - CT        │ Ex: SC2 - CT, HMPV - CT (3 casas, vírgula)            │
│ ... (repete para cada alvo do exame)                                        │
│                    │ Para VR1e2: 7 alvos × 2 colunas = 14 colunas         │
│                    │ Para ZDC: 6 alvos × 2 colunas = 12 colunas           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ CONTROLE GAL (STATUS E RASTREAMENTO)                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ status_gal         │ "não enviado" / "tipo nao enviavel" / "enviado"       │
│ mensagem_gal       │ Motivo se não enviável (Ex: controle)                 │
│ data_hora_envio    │ Timestamp do envio (NULL se não enviado)              │
│ usuario_envio      │ Quem fez o envio (NULL se não enviado)                │
│ sucesso_envio      │ True/False/NULL (indicador de sucesso)                │
│ detalhes_envio     │ Resposta do servidor ou erro (se houver)              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ AUDITORIA                                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ criado_em          │ Quando registro foi criado (imutável)                  │
│ atualizado_em      │ Quando foi atualizado pela última vez                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 💾 Exemplo de Linha CSV Evoluída

### VR1e2 (7 alvos):

```csv
id_registro;data_hora_analise;usuario_analise;exame;lote;arquivo_corrida;poco;amostra;codigo;status_corrida;SC2 - R;SC2 - CT;HMPV - R;HMPV - CT;INF A - R;INF A - CT;INF B - R;INF B - CT;ADV - R;ADV - CT;RSV - R;RSV - CT;HRV - R;HRV - CT;RP1 - CT;status_gal;mensagem_gal;data_hora_envio;usuario_envio;sucesso_envio;detalhes_envio;criado_em;atualizado_em

550e8400-e29b-41d4-a716-446655440000;2025-12-05 19:54:54;márcio;vr1e2_biomanguinhos_7500;;201205_1930.csv;A1+A2;422386;422386149;Válida;SC2 - 1;38,456;HMPV - 2;;INF A - 1;35,200;INF B - 2;;ADV - 1;32,100;RSV - 2;;HRV - 3;37,500;25,500;não enviado;;;FALSE;;2025-12-05 19:54:54;2025-12-05 19:54:54

550e8400-e29b-41d4-a716-446655440001;2025-12-05 19:54:54;márcio;vr1e2_biomanguinhos_7500;;201205_1930.csv;B1+B2;422387;422387254;Válida;SC2 - 2;;HMPV - 1;35,600;INF A - 2;;INF B - 1;33,200;ADV - 2;;RSV - 1;30,400;HRV - 2;;30,200;enviado;codigo 422387254;2025-12-05 20:15:00;márcio;TRUE;Enviado com sucesso;2025-12-05 19:54:54;2025-12-05 20:15:00
```

### ZDC (6 alvos, diferentes):

```csv
550e8400-e29b-41d4-a716-446655440002;2025-12-05 20:00:00;márcio;zdc_biomanguinhos_7500;;201205_2000.csv;A1+A2;422500;422500100;Válida;DEN1 - 1;36,200;DEN2 - 2;;DEN3 - 1;34,500;DEN4 - 2;;ZYK - 1;31,200;CHIK - 2;;não enviado;;;FALSE;;2025-12-05 20:00:00;2025-12-05 20:00:00
```

---

## 🔧 Implementação Passo a Passo

### PASSO 1: Migração do CSV Existente

**Objetivo:** Adicionar novos campos sem perder dados

```python
# scripts/migrate_historical_csv.py

import pandas as pd
import uuid
from pathlib import Path

def migrate_historical_csv():
    """
    Migra CSV histórico existente adicionando:
    - id_registro (UUID)
    - data_hora_envio (NULL)
    - usuario_envio (NULL)
    - sucesso_envio (FALSE)
    - detalhes_envio (vazio)
    """
    
    csv_path = Path("logs/historico_analises.csv")
    
    # 1. Lê CSV existente
    df = pd.read_csv(csv_path, sep=";", encoding="utf-8")
    
    # 2. Adiciona novos campos no início (após campos de rastreabilidade)
    # Reordena as colunas para ficar: ID, rastreabilidade, dados, resultados, GAL, auditoria
    
    df.insert(0, "id_registro", [str(uuid.uuid4()) for _ in range(len(df))])
    
    # 3. Adiciona colunas de rastreamento de envio
    df["data_hora_envio"] = None
    df["usuario_envio"] = None
    df["sucesso_envio"] = False
    df["detalhes_envio"] = ""
    
    # 4. Se status_gal for "tipo nao enviavel", marca sucesso_envio como NULL
    df.loc[df["status_gal"] == "tipo nao enviavel", "sucesso_envio"] = None
    
    # 5. Renomeia status_gal para melhor semântica
    df["status_gal"] = df["status_gal"].replace({
        "analizado e nao enviado": "não enviado",
        "tipo nao enviavel": "não enviável"
    })
    
    # 6. Backup do arquivo original
    csv_backup = csv_path.with_suffix(".backup_20251207.csv")
    df_original = pd.read_csv(csv_path, sep=";", encoding="utf-8")
    df_original.to_csv(csv_backup, sep=";", index=False, encoding="utf-8")
    print(f"✅ Backup criado: {csv_backup}")
    
    # 7. Escreve novo CSV
    df.to_csv(csv_path, sep=";", index=False, encoding="utf-8")
    print(f"✅ CSV migrado: {csv_path}")
    print(f"   Linhas: {len(df)}")
    print(f"   Colunas: {len(df.columns)}")
    
    return df

if __name__ == "__main__":
    migrate_historical_csv()
```

---

### PASSO 2: Atualizar `gerar_historico_csv()` para Múltiplos Exames

**Arquivo:** `services/history_report.py`

```python
import uuid
from datetime import datetime

def gerar_historico_csv(
    df_final: pd.DataFrame,
    exame: str,
    usuario: str,
    lote: str = "",
    arquivo_corrida: str = "",
    caminho_csv: str = "logs/historico_analises.csv",
) -> None:
    """
    Versão evoluída que:
    - Suporta QUALQUER exame (lê config do registry)
    - Gera ID único para cada registro
    - Inicializa campos de rastreamento GAL
    - Mantém compatibilidade com CSV anterior
    """
    
    cfg = get_exam_cfg(exame)
    
    if cfg is None:
        raise ValueError(f"Exame '{exame}' não encontrado no registry")
    
    # ... (mesmo processamento anterior para alvos/CTs/mapeamento)
    
    linhas = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for _, r in df_final.iterrows():
        codigo = str(r.get("Codigo", "")).strip()
        amostra = str(r.get("Amostra", "")).strip()
        poco = str(r.get("Poco", "")).strip()
        status_corrida = str(r.get("Status_Corrida", "")).strip()
        
        # ✅ NOVO: Gera ID único para cada registro
        id_registro = str(uuid.uuid4())
        
        status_gal = "não enviado"  # Default: sempre começa como não enviado
        mensagem_gal = ""
        
        cod_lower = codigo.lower()
        if (not codigo.isdigit()) or ("cn" in cod_lower) or ("cp" in cod_lower):
            status_gal = "não enviável"
            mensagem_gal = "Código não numérico ou controle"
        
        # ✅ NOVA ESTRUTURA DE LINHA
        linha = {
            # Identificação e rastreabilidade
            "id_registro": id_registro,
            "data_hora_analise": timestamp,
            "usuario_analise": usuario,
            "exame": exame,
            "lote": lote or "",
            "arquivo_corrida": arquivo_corrida or "",
            
            # Dados da amostra
            "poco": poco,
            "amostra": amostra,
            "codigo": codigo,
            "status_corrida": status_corrida,
            
            # [Aqui vêm SC2 - R, SC2 - CT, HMPV - R, etc. - conforme exame]
            # (mesmo código anterior de mapeamento)
            
            # ✅ NOVO: Controle GAL
            "status_gal": status_gal,
            "mensagem_gal": mensagem_gal,
            "data_hora_envio": None,      # Preenchido apenas após envio
            "usuario_envio": None,         # Preenchido apenas após envio
            "sucesso_envio": None,         # None=não enviável, False=falha, True=sucesso
            "detalhes_envio": "",          # Resposta do servidor
            
            # Auditoria
            "criado_em": timestamp,
            "atualizado_em": timestamp,
        }
        
        # ... (resto do processamento igual)
        
        linhas.append(linha)
    
    if not linhas:
        return
    
    df_hist = pd.DataFrame(linhas)
    
    # ✅ NOVO: Se arquivo existe, verifica se precisa adicionar colunas faltantes
    if os.path.exists(caminho_csv):
        df_existente = pd.read_csv(caminho_csv, sep=";", encoding="utf-8")
        
        # Colunas que devem estar sempre presentes
        colunas_esperadas = set(df_hist.columns)
        colunas_existentes = set(df_existente.columns)
        
        # Se faltam colunas no CSV (ex: primeira vez com novo exame)
        if colunas_existentes != colunas_esperadas:
            # Adiciona colunas faltantes no histórico anterior
            for col in colunas_esperadas - colunas_existentes:
                df_existente[col] = None
            
            # Reordena para compatibilidade
            df_existente = df_existente[colunas_esperadas]
            
            # Escreve de novo
            df_existente.to_csv(
                caminho_csv,
                sep=";",
                index=False,
                encoding="utf-8"
            )
    
    # Escreve novas linhas
    os.makedirs(os.path.dirname(caminho_csv), exist_ok=True)
    header = not os.path.exists(caminho_csv)
    df_hist.to_csv(
        caminho_csv,
        sep=";",
        index=False,
        mode="a",
        header=header,
        encoding="utf-8"
    )
```

---

### PASSO 3: Nova Função para Atualizar Status GAL

**Arquivo:** `services/history_report.py` (nova função)

```python
def atualizar_status_gal(
    csv_path: str,
    id_registros: List[str],  # IDs dos registros a atualizar
    sucesso: bool,
    usuario_envio: str,
    detalhes: str = ""
) -> int:
    """
    Atualiza status_gal de registros após envio para o GAL.
    
    Args:
        csv_path: Caminho do histórico CSV
        id_registros: Lista de IDs para atualizar
        sucesso: True se envio foi bem-sucedido
        usuario_envio: Quem fez o envio
        detalhes: Mensagem de resposta/erro
    
    Returns:
        Número de registros atualizados
    """
    
    # 1. Lê o CSV completo
    df = pd.read_csv(csv_path, sep=";", encoding="utf-8")
    
    timestamp_envio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    registros_atualizados = 0
    
    # 2. Para cada ID fornecido
    for id_reg in id_registros:
        mask = df["id_registro"] == id_reg
        
        if not mask.any():
            registrar_log(
                "Histórico GAL",
                f"ID {id_reg} não encontrado no CSV",
                "WARNING"
            )
            continue
        
        # 3. Atualiza campos de envio
        df.loc[mask, "status_gal"] = "enviado" if sucesso else "falha no envio"
        df.loc[mask, "data_hora_envio"] = timestamp_envio
        df.loc[mask, "usuario_envio"] = usuario_envio
        df.loc[mask, "sucesso_envio"] = sucesso
        df.loc[mask, "detalhes_envio"] = detalhes
        df.loc[mask, "atualizado_em"] = timestamp_envio
        
        registros_atualizados += 1
    
    # 4. Escreve de volta (sobrescreve)
    df.to_csv(csv_path, sep=";", index=False, encoding="utf-8")
    
    registrar_log(
        "Histórico GAL",
        f"{registros_atualizados} registros atualizados",
        "INFO"
    )
    
    return registros_atualizados
```

---

### PASSO 4: Integrar com Módulo de Envio GAL

**Arquivo:** `exportacao/envio_gal.py` (modificar após envio bem-sucedido)

```python
def enviar_amostras_gal(
    df_amostras: pd.DataFrame,
    usuario_logado: str,
    callback_sucesso=None
):
    """
    Após envio bem-sucedido, atualiza histórico.
    """
    
    # ... (código de envio existente)
    
    if sucesso_envio:  # Se enviou com sucesso
        # ✅ NOVO: Atualiza histórico CSV
        from services.history_report import atualizar_status_gal
        
        # Obtém IDs dos registros que foram enviados
        ids_enviados = df_amostras.get("id_registro", []).tolist()
        
        atualizar_status_gal(
            csv_path="logs/historico_analises.csv",
            id_registros=ids_enviados,
            sucesso=True,
            usuario_envio=usuario_logado,
            detalhes="Enviado com sucesso para GAL"
        )
        
        if callback_sucesso:
            callback_sucesso()
    else:
        # Se falhou
        from services.history_report import atualizar_status_gal
        
        ids_enviados = df_amostras.get("id_registro", []).tolist()
        
        atualizar_status_gal(
            csv_path="logs/historico_analises.csv",
            id_registros=ids_enviados,
            sucesso=False,
            usuario_envio=usuario_logado,
            detalhes=f"Erro: {erro_detalhes}"
        )
```

---

## 📊 Fluxo de Dados Completo (Evoluído)

```
┌──────────────────────────────────────┐
│ ANÁLISE REALIZADA                    │
│ Exame: VR1e2, ZDC, VR1, etc.       │
│ 32 amostras com alvos específicos    │
└──────────────────────┬───────────────┘
                       ▼
┌──────────────────────────────────────┐
│ gerar_historico_csv()                │
│ • Valida amostras                    │
│ • Gera UUID (id_registro)            │
│ • Mapeia alvos específicos do exame  │
│ • Status_gal = "não enviado"        │
│ • data_hora_envio = NULL             │
└──────────────────────┬───────────────┘
                       ▼
┌──────────────────────────────────────┐
│ CSV: historico_analises.csv          │
│ (APPEND - adiciona 32 linhas)        │
│                                      │
│ Linha 1: id=UUID1, status=não envi. │
│ Linha 2: id=UUID2, status=não envi. │
│ ...                                  │
│ Linha 32: id=UUID32, status=não env.│
└──────────────────────┬───────────────┘
                       ▼
┌──────────────────────────────────────┐
│ MAIS TARDE: Usuário envia para GAL   │
│ • Seleciona amostras no histórico    │
│ • Clica "Enviar para GAL"            │
└──────────────────────┬───────────────┘
                       ▼
┌──────────────────────────────────────┐
│ envio_gal.py                         │
│ • Faz login no servidor              │
│ • Envia dados                        │
│ • Aguarda resposta                   │
└──────────────────────┬───────────────┘
                       ▼
┌──────────────────────────────────────┐
│ Resposta do Servidor: OK/ERRO        │
└──────────────────────┬───────────────┘
                       ▼
┌──────────────────────────────────────┐
│ atualizar_status_gal()               │
│ • Lê id_registros (UUIDs)            │
│ • data_hora_envio = NOW              │
│ • usuario_envio = márcio             │
│ • sucesso_envio = True/False         │
│ • detalhes_envio = "OK" ou erro      │
│ • status_gal = "enviado" ou "erro"  │
└──────────────────────┬───────────────┘
                       ▼
┌──────────────────────────────────────┐
│ CSV: historico_analises.csv          │
│ (SOBRESCREVE linhas dos UUIDs)       │
│                                      │
│ Linha 1:                             │
│ status_gal=enviado                   │
│ data_hora_envio=2025-12-05 20:15:00 │
│ usuario_envio=márcio                 │
│ sucesso_envio=TRUE                   │
└──────────────────────────────────────┘
```

---

## ✅ Checklist de Implementação

- [ ] **PASSO 1:** Criar script de migração (migrate_historical_csv.py)
- [ ] **PASSO 2:** Rodar migração (backup automático criado)
- [ ] **PASSO 3:** Atualizar gerar_historico_csv() com UUID e novos campos
- [ ] **PASSO 4:** Implementar atualizar_status_gal()
- [ ] **PASSO 5:** Integrar com envio_gal.py
- [ ] **PASSO 6:** Testar com VR1e2 (existente)
- [ ] **PASSO 7:** Testar com ZDC (novo exame)
- [ ] **PASSO 8:** Verificar que campos dinâmicos são criados corretamente
- [ ] **PASSO 9:** Validar que histórico pode ser visualizado
- [ ] **PASSO 10:** Documentar novo fluxo

---

## 🎯 Benefícios dessa Abordagem

| Aspecto | Benefício |
|---------|-----------|
| **Escalabilidade** | Suporta ilimitados exames sem mudança estrutural |
| **Rastreabilidade** | UUID + timestamps para auditoria completa |
| **Compatibilidade** | CSV é formato universal, fácil de importar/exportar |
| **Manutenibilidade** | Lógica centralizada, sem duplicação |
| **Sem Breaking Changes** | Dados antigos continuam válidos |
| **Simples** | Sem BD complexa, apenas CSV com novos campos |
| **Resiliente** | Se BD falha, CSV é fallback perfeito |

---

## 🚨 Pontos de Atenção

1. **Performance CSV:** Com muitos registros (>10k), considerar sharding por data
2. **Concorrência:** Se múltiplos processos escrevem ao mesmo tempo, usar lock
3. **Backup:** Fazer backup automático do CSV antes de migração
4. **Validação:** Verificar integridade após migração (comparar linhas)

---

## 📚 Próximos Passos

Deseja que eu:
1. Crie os scripts prontos para executar?
2. Implemente as mudanças no código?
3. Crie um sistema de backup automático?
4. Adicione validação de integridade?
