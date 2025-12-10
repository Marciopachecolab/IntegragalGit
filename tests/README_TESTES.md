# 🧪 Scripts de Teste - Fase 1

Scripts para validar as correções críticas implementadas na Fase 1.

---

## 📋 Testes Disponíveis

### 1️⃣ **test_nan_bug.py** - Teste de NaN após salvar mapa

**O que testa:**
- ✅ `to_dataframe()` retorna resultados em formato completo ("Detectado", não "Det")
- ✅ Merge preserva resultados sem criar colunas `_BACKUP`
- ✅ Nenhum valor NaN é gerado no processo
- ✅ Tipos de dados permanecem corretos (`object`, não numérico)

**Como executar:**
```powershell
python tests/test_nan_bug.py
```

**Resultado esperado:**
```
====================================================================
TESTE 1: to_dataframe() preserva resultados textuais
====================================================================
✅ Todos os tipos corretos (object)
✅ Nenhum NaN encontrado
✅ Todos os resultados em formato completo

====================================================================
TESTE 2: Merge preserva resultados (sem criar _BACKUP)
====================================================================
✅ Nenhuma coluna _BACKUP criada
✅ Colunas corretas
✅ Nenhum NaN
✅ Merge funciona corretamente

🎉🎉🎉🎉🎉 TODOS OS TESTES PASSARAM! 🎉🎉🎉🎉🎉
```

---

### 2️⃣ **test_vsr_export.py** - Teste de exportação VSR para GAL

**O que testa:**
- ✅ Aliases VSR/RSV estão presentes no código
- ✅ `formatar_para_gal()` exporta coluna `vsincicialresp`
- ✅ `formatar_multi_painel_gal()` exporta coluna `vsincicialresp` (CRÍTICO)
- ✅ Valores são mapeados corretamente (1=Detectado, 2=Não Detectado)

**Como executar:**
```powershell
python tests/test_vsr_export.py
```

**Resultado esperado:**
```
====================================================================
TESTE 1: Aliases VSR/RSV no gal_formatter
====================================================================
✅ "VSINCICIALRESP" encontrado
✅ "VSR" encontrado
✅ "RSV" encontrado

====================================================================
TESTE 2: Exportação VSR com formatar_para_gal()
====================================================================
✅ Coluna 'vsincicialresp' presente
✅ S002 (RSV Detectado) → vsincicialresp = '1'
✅ Valor correto (1 = Detectado)

====================================================================
TESTE 3: Exportação VSR com formatar_multi_painel_gal()
====================================================================
✅ Coluna 'vsincicialresp' presente
✅ S101 (RSV Detectado) → vsincicialresp = '1'

🎉🎉🎉🎉🎉 TODOS OS TESTES DE VSR PASSARAM! 🎉🎉🎉🎉🎉
```

---

## 🚀 Executar Todos os Testes

**Windows PowerShell:**
```powershell
# Ativar ambiente virtual
& C:/Users/marci/Desktop/venv/Scripts/Activate.ps1

# Executar ambos os testes
python tests/test_nan_bug.py
python tests/test_vsr_export.py
```

**Ou criar script batch:**
```powershell
# criar arquivo run_all_tests.ps1
@"
& C:/Users/marci/Desktop/venv/Scripts/Activate.ps1
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Executando teste de NaN..." -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
python tests/test_nan_bug.py

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Executando teste de VSR..." -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
python tests/test_vsr_export.py
"@ | Out-File -FilePath run_all_tests.ps1

# Executar
.\run_all_tests.ps1
```

---

## 🧪 Teste Manual Completo

### Cenário 1: Editar Mapa e Salvar

1. **Executar sistema:**
   ```powershell
   python main.py
   ```

2. **Processar um run:**
   - Carregar arquivo de análise
   - Aguardar conclusão

3. **Abrir mapa da placa:**
   - Na janela de análise, clicar em "🧬 Mapa da Placa"

4. **Editar um valor:**
   - Selecionar um poço (ex: A01)
   - Alterar CT de SC2 (ex: 25.5 → 30.0)
   - Clicar "Aplicar"
   - Clicar "💾 Salvar Alterações e Voltar"

5. **Verificar aba de análise:**
   - Voltar para "📊 Análise"
   - **VERIFICAR:** Coluna `Resultado_SC2` deve mostrar "Detectado"/"Não Detectado" (não NaN)

6. **Verificar logs:**
   ```powershell
   Get-Content logs/sistema.log -Tail 50 | Select-String "Sync|DEBUG_MERGE"
   ```
   
   **Deve mostrar:**
   ```
   [DEBUG] ANTES - df_analise: 36 linhas, 21 colunas
   [DEBUG] df_updated: 36 linhas, 21 colunas
   [DEBUG] DEPOIS - Merge concluído: 36 linhas, 21 colunas
   [DEBUG] DEPOIS - Tipos de dados: {'Resultado_SC2': 'object', ...}
   ```
   
   **NÃO DEVE mostrar:**
   ```
   [ERROR] ERRO CRÍTICO: X valores NaN
   [WARNING] AVISO: X NaN detectados em Resultado_*
   ```

---

### Cenário 2: Exportar VSR para GAL

1. **Processar run com RSV positivo:**
   - Garantir que pelo menos uma amostra tem `Resultado_RSV = "Detectado"`

2. **Exportar para GAL:**
   - Menu: Exportar → GAL CSV
   - Salvar arquivo

3. **Verificar CSV gerado:**
   ```powershell
   # Abrir CSV
   Import-Csv "reports/gal_last_exame.csv" -Delimiter ";" | 
       Select-Object registroInterno, vsincicialresp | 
       Format-Table
   ```
   
   **Deve mostrar:**
   ```
   registroInterno  vsincicialresp
   ---------------  --------------
   1001             2
   1002             1              <-- RSV Detectado
   1003             2
   ```

4. **Verificar logs:**
   ```powershell
   Get-Content logs/sistema.log | Select-String "Export GAL|vsincicialresp"
   ```

---

## ❌ Troubleshooting

### Teste falha com "ModuleNotFoundError"
```powershell
# Verificar que está no diretório correto
cd C:\Users\marci\Downloads\Integragal

# Verificar ambiente virtual ativo
python -c "import sys; print(sys.prefix)"
```

### Teste falha com "AssertionError: Valores abreviados encontrados"
**Problema:** `to_dataframe()` ainda retorna "Det"/"ND" ao invés de "Detectado"/"Não Detectado"

**Solução:** Implementar denormalização (Fase 3 opcional) ou verificar se `normalize_result()` está sendo aplicado incorretamente.

### Teste VSR falha com "Coluna vsincicialresp não encontrada"
**Problema:** Aliases VSR não foram adicionados na segunda `_find_result_col()`

**Solução:** Verificar linha 303 de `exportacao/gal_formatter.py`:
```python
aliases = {
    ...
    "VSINCICIALRESP": "RSV",  # <-- DEVE ESTAR PRESENTE
    "VSR": "RSV",              # <-- DEVE ESTAR PRESENTE
}
```

---

## 📊 Critérios de Sucesso

**✅ Fase 1 completa quando:**
1. ✅ `test_nan_bug.py` passa sem erros
2. ✅ `test_vsr_export.py` passa sem erros
3. ✅ Teste manual de edição do mapa não gera NaN
4. ✅ Teste manual de exportação GAL contém `vsincicialresp` preenchido
5. ✅ Logs mostram merge estável (21→21 colunas, sem _BACKUP)

---

## 📝 Próximas Etapas

Após todos os testes passarem:
- [ ] Documentar resultados no histórico do projeto
- [ ] Commit das correções no Git
- [ ] (Opcional) Implementar Fase 3: denormalização de resultados
- [ ] (Opcional) Criar testes de integração E2E
