# TESTE AUTOMÁTICO COMPLETO - Integragal VR1E2
**Arquivo**: `tests/test_fluxo_completo_real.py`

## 📋 Descrição

Este teste automatiza **COMPLETAMENTE** o fluxo de análise VR1E2 Biomanguinhos, eliminando a necessidade de testes manuais. Ele simula exatamente o que acontece na interface gráfica.

## 🎯 O Que o Teste Faz

### 1. **Carrega Mapeamento Real**
- Lê `mapeamento_teste.txt` com amostras reais
- Valida estrutura (Poco, Amostra, Codigo)

### 2. **Executa Análise Completa**
- Lê arquivo Excel real: `C:\Users\marci\Downloads\18 JULHO 2025\20250718 VR1-VR2 BIOM PLACA 5.xlsx`
- Processa todos os 7 alvos (SC2, HMPV, INF A, INF B, ADV, RSV, HRV)
- Valida controles CN/CP
- Retorna DataFrame com resultados

### 3. **Simula Edição no Mapa da Placa**
- Cria `PlateModel` a partir do DataFrame
- **Altera CT de SC2 para 11** (simulando edição manual do usuário)
- Aplica `recompute_all()` (equivalente a clicar "Aplicar")
- Converte de volta para DataFrame com `to_dataframe()` (equivalente a "Salvar")

### 4. **Valida Merge Sem NaN**
- Simula callback `_on_mapa_salvo()` da janela de análise
- Faz merge preservando apenas coluna "Selecionado"
- **Verifica que NÃO há NaN** em nenhuma coluna de resultado
- Valida tipos de dados (object, não float)

### 5. **Valida Exportação GAL**
- Formata DataFrame para padrão GAL
- **Verifica que coluna `vsincicialresp` existe** (VSR exportado)
- Valida códigos de resultado (1=Detectado, 2=Não Detectado, 3=Inconclusivo)
- Confirma mapeamento de todos os alvos

## ✅ Validações Automáticas

| Validação | Descrição |
|-----------|-----------|
| ✅ Mapeamento | 48 linhas carregadas corretamente |
| ✅ Análise | Todos os alvos processados (SC2, HMPV, INF A, INF B, ADV, RSV, HRV) |
| ✅ Edição Mapa | CT de SC2 alterado para 11 no poço correto |
| ✅ **Sem NaN** | **Nenhum valor NaN após merge** |
| ✅ **VSR Export** | **Coluna vsincicialresp presente no GAL** |
| ✅ Códigos GAL | Mapeamento correto (Det→1, ND→2, Inc→3) |

## 🚀 Como Executar

### Teste Individual
```powershell
python tests/test_fluxo_completo_real.py
```

### Todos os Testes
```powershell
./run_all_tests.ps1
```

## 📂 Arquivos Necessários

1. **Mapeamento**: `mapeamento_teste.txt` (raiz do projeto)
2. **Corrida**: `C:\Users\marci\Downloads\18 JULHO 2025\20250718 VR1-VR2 BIOM PLACA 5.xlsx`

## 🔧 Configurações

Editar no topo do arquivo `test_fluxo_completo_real.py`:

```python
ARQUIVO_MAPEAMENTO = r"C:\Users\marci\Downloads\Integragal\mapeamento_teste.txt"
ARQUIVO_CORRIDA = r"C:\Users\marci\Downloads\18 JULHO 2025\20250718 VR1-VR2 BIOM PLACA 5.xlsx"
LOTE_TESTE = "6565656"
NOVO_CT_SC2 = 11.0  # Valor para simular edição manual
```

## 📊 Output Esperado

```
======================================================================
🚀 TESTE AUTOMÁTICO COMPLETO - Fluxo Real VR1E2
======================================================================

======================================================================
📋 ETAPA 1: Carregar Mapeamento
======================================================================
✅ Mapeamento carregado: 48 linhas

======================================================================
🧬 ETAPA 2: Executar Análise VR1E2 Biomanguinhos
======================================================================
✅ Análise concluída!
   Status: Valida
   - SC2: 6 Detectado, 28 Não Detectado
   - HMPV: 2 Detectado, 32 Não Detectado
   ...

======================================================================
🗺️  ETAPA 3: Simular Edição no Mapa da Placa
======================================================================
✅ Poço B07: CT_SC2 alterado de 19.21 para 11.0
✅ DataFrame atualizado criado

======================================================================
✅ ETAPA 4: Validar Merge (Simular _on_mapa_salvo)
======================================================================
✅ SUCESSO: Nenhum NaN encontrado!

======================================================================
📤 ETAPA 5: Validar Exportação GAL
======================================================================
✅ Coluna 'vsincicialresp' encontrada
✅ Exportação GAL validada!

======================================================================
📊 RESUMO DO TESTE
======================================================================
✅ Mapeamento carregado
✅ Análise executada
✅ Mapa editado (CT SC2 → 11.0)
✅ Merge sem NaN
✅ Exportação GAL com VSR

🎉 TODOS OS TESTES PASSARAM!
```

## 🐛 Correções Validadas

Este teste confirma que **AMBOS** os bugs foram corrigidos:

### Bug 1: NaN após salvar mapa ✅ CORRIGIDO
- **Causa**: Merge criando colunas duplicadas com sufixo `_BACKUP`
- **Correção**: Merge preserva apenas coluna "Selecionado"
- **Validação**: Teste verifica que não há NaN em nenhuma coluna de resultado

### Bug 2: VSR não exportado ✅ CORRIGIDO
- **Causa**: Faltavam aliases VSR na segunda `_find_result_col()` (linha 303)
- **Correção**: Adicionados aliases "VSINCICIALRESP", "VSINCICIALRESPA", "VSINCICIALRESPB", "VSR" → "RSV"
- **Validação**: Teste verifica presença de coluna `vsincicialresp` no CSV do GAL

## 🔄 Fluxo Simulado

```
┌─────────────────────┐
│  Mapeamento.txt     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Arquivo Excel      │
│  (VR1-VR2 PLACA 5)  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Análise VR1E2      │
│  (analisar_placa)   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  PlateModel         │
│  (from_df)          │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Editar CT SC2→11   │
│  (simula usuário)   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Aplicar + Salvar   │
│  (to_dataframe)     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Merge Callback     │
│  (_on_mapa_salvo)   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Exportar GAL       │
│  (formatar_para_gal)│
└─────────────────────┘
```

## 💡 Benefícios

1. **Zero Intervenção Manual**: Executa sozinho do início ao fim
2. **Validação Completa**: Testa análise + edição + merge + exportação
3. **Arquivo Real**: Usa dados reais de produção (não mocks)
4. **Reprodutível**: Sempre testa o mesmo cenário
5. **Rápido**: ~5 segundos vs. minutos de teste manual
6. **CI/CD Ready**: Pode rodar em pipeline automatizado

## 🎯 Uso Recomendado

Execute este teste **SEMPRE QUE**:
- Modificar `plate_viewer.py` (PlateModel, to_dataframe)
- Modificar `gal_formatter.py` (exportação GAL)
- Modificar `janela_analise_completa.py` (merge callback)
- Modificar `vr1e2_biomanguinhos_7500.py` (análise)
- Antes de deploy em produção

---

**Criado em**: Dezembro 10, 2025  
**Última atualização**: Dezembro 10, 2025  
**Versão**: 1.0
