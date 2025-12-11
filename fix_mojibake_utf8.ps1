# Script para corrigir mojibake e garantir UTF-8 sem BOM
# Autor: Sistema IntegRAGal
# Data: 2025-12-10

$ErrorActionPreference = "Continue"

# Mapeamento de correções mojibake comuns
$mojibakeMap = @{
    'Ã§' = 'ç'
    'Ã£' = 'ã'
    'Ã©' = 'é'
    'Ã­' = 'í'
    'Ã³' = 'ó'
    'Ãº' = 'ú'
    'Ã¡' = 'á'
    'Ã ' = 'à'
    'Ã¢' = 'â'
    'Ãª' = 'ê'
    'Ã´' = 'ô'
    'Ã' = 'Ã'
    'Ã‡' = 'Ç'
    'Ãƒ' = 'Ã'
    'Ã‰' = 'É'
    'Ãš' = 'Ú'
    'â€"' = '—'
    'â€"' = '–'
    'â€œ' = '"'
    'â€' = '"'
    'â€™' = "'"
    'â€˜' = "'"
    'â€¦' = '…'
    'â†'' = '→'
    'â""' = '└'
    'â"€' = '─'
    'âœ"' = '✓'
    'âœ…' = '✅'
    'â­•' = '⭕'
    'â„¢' = '™'
    'Â°' = '°'
    'Â´' = '´'
    'Â«' = '«'
    'Â»' = '»'
}

$totalFiles = 0
$fixedFiles = 0
$errorFiles = 0

Write-Host "=== Corrigindo Mojibake e convertendo para UTF-8 sem BOM ===" -ForegroundColor Cyan
Write-Host ""

# Processar todos os arquivos Python
Get-ChildItem -Recurse -Filter "*.py" | Where-Object { 
    $_.FullName -notlike "*__pycache__*" -and 
    $_.FullName -notlike "*venv*" -and
    $_.FullName -notlike "*.git*"
} | ForEach-Object {
    $totalFiles++
    $filePath = $_.FullName
    $fileName = $_.Name
    
    try {
        # Ler arquivo com encoding UTF-8
        $content = [System.IO.File]::ReadAllText($filePath, [System.Text.Encoding]::UTF8)
        
        $originalContent = $content
        $hasMojibake = $false
        
        # Aplicar correções de mojibake
        foreach ($key in $mojibakeMap.Keys) {
            if ($content -like "*$key*") {
                $hasMojibake = $true
                $content = $content.Replace($key, $mojibakeMap[$key])
            }
        }
        
        # Salvar com UTF-8 sem BOM (sempre, mesmo que não tenha mojibake)
        $utf8NoBom = New-Object System.Text.UTF8Encoding $false
        [System.IO.File]::WriteAllText($filePath, $content, $utf8NoBom)
        
        if ($hasMojibake) {
            Write-Host "✓ CORRIGIDO: $fileName" -ForegroundColor Green
            $fixedFiles++
        } else {
            Write-Host "  OK: $fileName" -ForegroundColor Gray
        }
        
    } catch {
        Write-Host "✗ ERRO: $fileName - $($_.Exception.Message)" -ForegroundColor Red
        $errorFiles++
    }
}

Write-Host ""
Write-Host "=== Resumo ===" -ForegroundColor Cyan
Write-Host "Total de arquivos: $totalFiles"
Write-Host "Arquivos corrigidos: $fixedFiles" -ForegroundColor Green
Write-Host "Arquivos com erro: $errorFiles" -ForegroundColor Red
Write-Host ""
Write-Host "Concluído!" -ForegroundColor Cyan
