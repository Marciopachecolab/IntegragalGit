Resumindo em uma frase: o `plate_viewer.py` está funcionando exatamente como foi programado, mas o **formato atual do `historico_analises.csv` não fornece CT numérico por alvo na maior parte das linhas**, então o mapa da placa acaba ficando sem CT (ou com CT “errado” em relação ao que você esperava ver).

Vou te mostrar onde isso aparece, passo a passo, dentro do código e do CSV.

---

## 1. O que o `plate_viewer.py` faz para buscar CT

No `PlateModel.from_df`, o fluxo para montar os dados de cada poço é assim:

1. Ele copia o `df_final` para `df_use` e monta dois dicionários:

```python
cols_upper = {c: str(c).upper() for c in df_use.columns}
cols_lower = {str(c).lower(): c for c in df_use.columns}
```

2. Se não tiver coluna de poço (`Poco` / `POCO`), mas tiver `WELL`, ele chama `_convert_df_norm` para normalizar um `df_norm` por poço/alvo em algo “df_final-like” (com colunas `Poco`, `Amostra`, `Codigo`, `Resultado_<ALVO>`, `CT_<ALVO>`).

3. Em seguida ele descobre os **alvos** olhando os nomes das colunas:

```python
targets: List[str] = []
for col in df_use.columns:
    cu = cols_upper[col]
    if cu.startswith("RESULTADO_"):
        alvo = cu.replace("RESULTADO_", "").strip()
        ...
    elif cu.endswith(" - R") or cu.endswith("- R") or cu.endswith(" - R".upper()):
        base = cu.replace(" - R", "").replace("- R", "").strip()
        if base and base not in targets:
            targets.append(base)
```

Com o seu `reports/historico_analises.csv`, isso vira:

```text
targets = ["SC2", "HMPV", "INFA", "INFB", "ADV", "RSV", "HRV"]
```

4. Antes dos alvos, ele monta os CT de RP:

```python
rp_ct_cols = []
for c in df_use.columns:
    cu = cols_upper.get(c, "")
    if ("RP" in cu) and ("CT" in cu) and (not cu.startswith("CT_RP")):
        rp_ct_cols.append(c)

for rp_col in rp_ct_cols:
    try:
        ct_val = row.get(rp_col, None)
        ct_val = float(str(ct_val).replace(",", "."))
    except Exception:
        ct_val = None
    rp_key = rp_col.split()[0].upper().replace("-", "_").replace(" ", "_")
    target_data[rp_key] = TargetResult("", ct_val)
```

Com o seu CSV, isso vira:

* `rp_ct_cols = ["RP_1 - CT", "RP_2 - CT"]`
* `target_data["RP_1"].ct` = valor numérico do `RP_1 - CT`
* `target_data["RP_2"].ct` = valor numérico do `RP_2 - CT`

Isso está **correto** e 100% coerente com os dados do `historico_analises.csv`.

5. Depois, para **cada alvo SC2, HMPV, INFA…**, ele faz:

```python
for alvo in targets:
    # Resultado
    res_col = f"Resultado_{alvo}"
    res_val = row.get(res_col, "")
    if not res_val:
        alt_col = f"{alvo} - R"
        res_val = row.get(alt_col, "")

    norm_res = normalize_result(str(res_val))

    # CT do alvo
    ct_val = None
    for c in df_use.columns:
        cu = cols_upper[c]
        if alvo.replace(" ", "") in cu.replace(" ", "") and "CT" in cu and not str(row.get(c, "")).strip() == "":
            try:
                ct_val = float(str(row.get(c)).replace(",", "."))
                break
            except Exception:
                ct_val = None

    target_data[alvo] = TargetResult(norm_res, ct_val)
```

Ou seja:

* ele procura **primeiro** um `Resultado_<ALVO>`; se não existir, cai no padrão `<ALVO> - R`;
* depois procura **qualquer coluna** que contenha o nome do alvo e “CT” ao mesmo tempo (ex.: `"SC2"` dentro de `"SC2 - CT"`), e que não esteja vazia, e converte para `float`.

---

## 2. O que o seu `historico_analises.csv` realmente tem

No `reports/historico_analises.csv`, o cabeçalho relevante é:

```text
poco, amostra, codigo, status_corrida, status_gal, ...
SC2 - R, SC2 - CT,
HMPV - R, HMPV - CT,
INFA - R, INFA - CT,
INFB - R, INFB - CT,
ADV - R, ADV - CT,
RSV - R, RSV - CT,
HRV - R, HRV - CT,
RP_1 - CT, RP_2 - CT
```

Quando olhamos as primeiras linhas, aparece algo dessa forma (resumo):

```text
linha 0:
  poco        = A1
  SC2 - R     = "SC2 - 2"
  SC2 - CT    = NaN
  RP_1 - CT   = 27,946
  RP_2 - CT   = 28,164

linha 25:
  poco        = B7+B8
  SC2 - R     = "SC2 - 1"
  SC2 - CT    = 19,213
  RP_1 - CT   = 19,213
  RP_2 - CT   = 19,213
```

Quando eu aplico exatamente a lógica do `plate_viewer.py` sobre essas linhas, o que sai é (em termos de `TargetResult`):

* **Linha 0 (amostra negativa)**

  * `SC2.result` = `"SC2 - 2"` (porque não existe `Resultado_SC2`)
  * `SC2.ct` = `None` (a coluna `SC2 - CT` está vazia)
  * `RP_1.ct` = `27.946`
  * `RP_2.ct` = `28.164`

* **Linha 25 (provável controle ou amostra positiva)**

  * `SC2.result` = `"SC2 - 1"`
  * `SC2.ct` = `19.213` (vem de `SC2 - CT`)
  * `RP_1.ct` = `19.213`
  * `RP_2.ct` = `19.213`

Ou seja:

* **Para os poços positivos** (onde existe célula numérica em `<ALVO> - CT`), o CT do alvo está sendo lido corretamente.
* **Para a maioria dos poços** (negativos ou onde o seu pipeline não gravou CT do alvo), as colunas `<ALVO> - CT` estão vazias, então o código deixa o CT do alvo como `None`.

Isso combina exatamente com o que você está vendo na GUI:
– Os RPs sempre têm CT;
– Os alvos principais só têm CT em alguns poços;
– Em vez de “Detectado / Não Detectado / Inconclusivo / Inválido”, o `result` dos alvos vem como `"SC2 - 1"` / `"SC2 - 2"`, etc., porque é assim que o `historico_analises.csv` está escrito.

---

## 3. Então por que “não está pegando os CTs certos”?

Do ponto de vista puramente técnico:

1. **O código está procurando CT exatamente onde você disse que eles estariam** (colunas com `<ALVO>` + `"CT"` no nome).
2. No **arquivo real**, os CTs dos alvos estão:

   * Preenchidos apenas em algumas linhas (ex.: controles, alguns positivos),
   * Vazios na maioria das amostras, enquanto o CT do RP está sempre presente em `RP_1 - CT` / `RP_2 - CT`.

Resultado prático:

* No mapa, para muitos poços o alvo “SC2” aparece sem CT (ou seja, `None`), porque não existe valor numérico em `SC2 - CT`.
* O CT que você visualiza e que “parece correto” é o CT de RP, não o CT específico do alvo.
* Se a sua expectativa era “ver sempre um CT numérico no mapa para cada amostra”, o `historico_analises.csv` não contém essa informação da forma que o `plate_viewer.py` espera.

Além disso, há um segundo problema sutil:

* As colunas `<ALVO> - R` não estão em formato categórico (“Detectado / Não Detectado / …”), mas sim como códigos (`"SC2 - 1"`, `"SC2 - 2"`, `"HMPV - 2"`, etc.).
* O `normalize_result` não reconhece esses códigos, então o `status` interno do poço não vira `POSITIVE`, `NEGATIVE`, etc., mas fica exatamente como a string original (`"SC2 - 2"`), o que também pode afetar cores e interpretação.

---

## 4. Onde exatamente está o gargalo (resumindo)

Dentro de `PlateModel.from_df`:

* **Parte que está OK para RPs:**

```python
rp_ct_cols = []
for c in df_use.columns:
    cu = cols_upper.get(c, "")
    if ("RP" in cu) and ("CT" in cu) and (not cu.startswith("CT_RP")):
        rp_ct_cols.append(c)
...
target_data[rp_key] = TargetResult("", ct_val)
```

* **Parte que depende da existência de CT por alvo (e onde “faltam” dados no CSV):**

```python
for alvo in targets:
    res_col = f"Resultado_{alvo}"
    res_val = row.get(res_col, "")
    if not res_val:
        alt_col = f"{alvo} - R"
        res_val = row.get(alt_col, "")

    norm_res = normalize_result(str(res_val))

    ct_val = None
    for c in df_use.columns:
        cu = cols_upper[c]
        if alvo.replace(" ", "") in cu.replace(" ", "") and "CT" in cu and not str(row.get(c, "")).strip() == "":
            try:
                ct_val = float(str(row.get(c)).replace(",", "."))
                break
            except Exception:
                ct_val = None

    target_data[alvo] = TargetResult(norm_res, ct_val)
```

Esta parte **só funciona se houver um CT numérico por alvo** nas colunas de CT (seja `"SC2 - CT"`, `"CT_SC2"`, etc.). Quando isso não existe, o CT fica `None` — e isso é exatamente o que o seu CSV entrega para a maioria dos poços.

---

## 5. O que você pode fazer (sem inventar nada)

Sem mudar nenhuma lógica clínica (só olhando o que já está no código e nos dados), há três caminhos consistentes:

### Caminho A – Ajustar o pipeline que gera o `historico_analises.csv`

Se a intenção é que o **mapa da placa mostre sempre o CT do alvo**, então o ideal é:

* Garantir que, no momento de salvar o `historico_analises.csv`, sejam gravadas colunas `<ALVO> - CT` com os CTs reais de **SC2, HMPV, INFA, INFB, ADV, RSV, HRV**, e não apenas os CTs de RP.

Com isso, **nenhuma mudança seria necessária no `plate_viewer.py`**, porque ele já está preparado para ler `<ALVO> - CT` e funcionar bem.

### Caminho B – Passar diretamente um `df_norm` com coluna `ct` para o `PlateModel`

Você já tem, no fluxo de análise (`vr1e2_biomanguinhos_7500.py`), um `df_norm` com:

```python
df_norm = df_proc[['WELL', 'Target', 'CT']].copy()
df_norm = df_norm.rename(columns={
    'WELL': 'well',
    'Target': 'target_name',
    'CT': 'ct',
})
```

O `plate_viewer` tem o método `_convert_df_norm` justamente para transformar esse formato em algo “df_final-like” com `Resultado_<ALVO>` e `CT_<ALVO>`.

Se, em vez de construir o viewer a partir do `historico_analises.csv`, você o alimentar com esse `df_norm` recém-saído da análise, os CTs virão diretamente da coluna `ct`, sem depender das colunas `<ALVO> - CT` do histórico.

### Caminho C – Ajustar a leitura de resultados/CT dentro do `plate_viewer.py`

Se a sua intenção é:

* Para **poços negativos**, usar o CT do RP (`RP_1 - CT`) como referência exibida;
* E manter o CT do alvo quando existir;

você pode adaptar o bloco que define o `ct_val`, por exemplo, algo na linha de (em pseudocódigo, seguindo a lógica atual):

```python
# depois de procurar CT do alvo em colunas de CT
if ct_val is None and alvo == alvo_principal and "RP_1" in target_data:
    ct_val = target_data["RP_1"].ct
```

ou ajustar o que significa “CT exibido” na GUI (por exemplo, mostrar sempre **CT do RP** em um campo, e CT do alvo em outro, separando as coisas).

> Aqui, eu só estou descrevendo o que seria tecnicamente necessário **se** essa for a sua intenção; a decisão de usar CT de RP como substituto do CT do alvo é totalmente clínica/metodológica e foge do que está explicitamente nos arquivos — então eu não vou afirmar que essa é “a solução correta”, apenas que é o que o código teria de fazer para mostrar CT em todos os poços com base nos dados atuais.

---

## 6. Conclusão

* No estado atual:

  * O `plate_viewer.py` está lendo corretamente:

    * CTs de RP nas colunas `RP_1 - CT` e `RP_2 - CT`;
    * CTs de alvo nas colunas `<ALVO> - CT` quando elas têm um número.
  * A maior parte das linhas do `historico_analises.csv` **não tem CT numérico por alvo**, só por RP.
  * As colunas de resultado (<ALVO> - R) trazem códigos “SC2 - 1/2”, etc., que não entram no mapeamento `POSITIVE/NEGATIVE/...`.

Por isso, o mapa da placa “não pega os CTs corretos” na sua percepção: **os dados de CT do alvo não estão completos no histórico**, e o viewer, por construção, não inventa nem reaproveita CT de RP como CT de alvo.

Se você me disser qual é exatamente a regra desejada para:

* CT que deve aparecer para cada amostra (alvo, RP, média, fallback etc.);
* E como os códigos `"SC2 - 1"`, `"SC2 - 2"` devem ser interpretados (equivalentes a Detectado / Não Detectado / Inconclusivo / Inválido),

eu posso te devolver o trecho do `plate_viewer.py` já reescrito, linha a linha, para aderir exatamente ao comportamento que você quer.
