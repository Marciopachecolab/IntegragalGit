# Script para executar todos os testes da Fase 1

& C:/Users/marci/Desktop/venv/Scripts/Activate.ps1

Write-Host "`n" -NoNewline
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   TESTES FASE 1 - CORREÇÕES CRÍTICAS   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Teste 1: NaN Bug
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "  🧪 Teste 1: Bug de NaN após salvar mapa" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""

python tests/test_nan_bug.py
$test1_exit = $LASTEXITCODE

if ($test1_exit -eq 0) {
    Write-Host "`n✅ Teste 1 PASSOU!`n" -ForegroundColor Green
} else {
    Write-Host "`n❌ Teste 1 FALHOU!`n" -ForegroundColor Red
}

# Teste 2: VSR Export
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "  🧪 Teste 2: Exportação VSR para GAL" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""

python tests/test_vsr_export.py
$test2_exit = $LASTEXITCODE

if ($test2_exit -eq 0) {
    Write-Host "`n✅ Teste 2 PASSOU!`n" -ForegroundColor Green
} else {
    Write-Host "`n❌ Teste 2 FALHOU!`n" -ForegroundColor Red
}

# Teste 3: Fluxo Completo com Arquivo Real
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "  🧪 Teste 3: Fluxo Completo Real VR1E2" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""

python tests/test_fluxo_completo_real.py
$test3_exit = $LASTEXITCODE

if ($test3_exit -eq 0) {
    Write-Host "`n✅ Teste 3 PASSOU!`n" -ForegroundColor Green
} else {
    Write-Host "`n❌ Teste 3 FALHOU!`n" -ForegroundColor Red
}

# Resumo
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "            RESUMO DOS TESTES           " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($test1_exit -eq 0) {
    Write-Host "✅ Teste NaN Bug: PASSOU" -ForegroundColor Green
} else {
    Write-Host "❌ Teste NaN Bug: FALHOU" -ForegroundColor Red
}

if ($test2_exit -eq 0) {
    Write-Host "✅ Teste VSR Export: PASSOU" -ForegroundColor Green
} else {
    Write-Host "❌ Teste VSR Export: FALHOU" -ForegroundColor Red
}

if ($test3_exit -eq 0) {
    Write-Host "✅ Teste Fluxo Completo: PASSOU" -ForegroundColor Green
} else {
    Write-Host "❌ Teste Fluxo Completo: FALHOU" -ForegroundColor Red
}

Write-Host ""
if ($test1_exit -eq 0 -and $test2_exit -eq 0 -and $test3_exit -eq 0) {
    Write-Host "🎉 TODOS OS TESTES PASSARAM!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠️  ALGUNS TESTES FALHARAM" -ForegroundColor Red
    exit 1
}

if ($test2_exit -eq 0) {
    Write-Host "✅ Teste VSR Export: PASSOU" -ForegroundColor Green
} else {
    Write-Host "❌ Teste VSR Export: FALHOU" -ForegroundColor Red
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($test1_exit -eq 0 -and $test2_exit -eq 0) {
    Write-Host "🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉" -ForegroundColor Green
    Write-Host "  TODOS OS TESTES PASSARAM!" -ForegroundColor Green
    Write-Host "  Fase 1 concluída com sucesso!" -ForegroundColor Green
    Write-Host "🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠️  ALGUNS TESTES FALHARAM" -ForegroundColor Red
    Write-Host "   Revise os erros acima" -ForegroundColor Red
    exit 1
}
