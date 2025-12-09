# Padrão de Encoding - IntegRAGal

## UTF-8 Sem BOM

**TODOS os arquivos Python do projeto devem usar UTF-8 SEM BOM (Byte Order Mark)**

### Por que UTF-8 sem BOM?

1. **Compatibilidade**: UTF-8 sem BOM é o padrão universal do Python 3
2. **Git**: Evita problemas de diff e merge
3. **Portabilidade**: Funciona em Windows, Linux e macOS sem conversões
4. **Emojis**: Suporta caracteres Unicode (🔬, 📂, ✅, ❌, etc.)

### Verificação de BOM

Para verificar se um arquivo tem BOM:

```powershell
# Um arquivo
Get-Content -Path "arquivo.py" -Encoding Byte -TotalCount 3 | ForEach-Object { $_.ToString("X2") }

# UTF-8 COM BOM: EF BB BF
# UTF-8 SEM BOM: Primeiros bytes do conteúdo (ex: 22 22 22 para """)
```

### Forçar UTF-8 no Output do Terminal

Para scripts que usam emojis ou caracteres especiais no output:

```python
# -*- coding: utf-8 -*-
import sys
import io

# Forçar UTF-8 no output do terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
```

### VS Code Settings

Configuração no `.vscode/settings.json`:

```json
{
    "files.encoding": "utf8",
    "files.autoGuessEncoding": false,
    "[python]": {
        "files.encoding": "utf8"
    }
}
```

### Verificação em Massa

```powershell
# Verificar todos os arquivos Python em services/
Get-ChildItem -Path services\*.py | ForEach-Object {
    $bytes = Get-Content -Path $_.FullName -Encoding Byte -TotalCount 3
    $bom = if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        "COM BOM"
    } else {
        "SEM BOM"
    }
    Write-Host "$($_.Name): $bom"
}
```

## Status Atual

✅ **TODOS os arquivos em `services/` estão sem BOM** (verificado em 08/12/2025)

### Arquivos Verificados

- analysis_service.py
- equipment_detector.py
- equipment_registry.py
- equipment_extractors.py
- universal_engine.py
- plate_viewer.py
- config_loader.py
- menu_handler.py
- system_paths.py
- Todos os demais arquivos em services/

### Teste de Emojis

O arquivo `teste_extractors.py` foi atualizado para:
1. Declarar encoding UTF-8 no cabeçalho
2. Forçar UTF-8 no output do terminal
3. Exibir emojis corretamente no PowerShell

**Resultado**: ✅ Emojis exibidos corretamente (🔬, 📂, ✅, ❌, 📊, 📝, 🎯, 📋)

## Diretrizes para Novos Arquivos

1. **Sempre criar arquivos Python em UTF-8 sem BOM**
2. **Adicionar `# -*- coding: utf-8 -*-` no cabeçalho** (opcional mas recomendado)
3. **Para scripts com output de emojis**: usar o wrapper de sys.stdout/stderr
4. **Nunca salvar com BOM**: verificar configuração do editor

## Conversão de Arquivos com BOM

Se encontrar arquivo com BOM:

```powershell
# Remover BOM de um arquivo
$content = Get-Content -Path "arquivo.py" -Raw
[System.IO.File]::WriteAllText("arquivo.py", $content, [System.Text.UTF8Encoding]::new($false))
```

Ou usar ferramentas:
- VS Code: "Save with Encoding" → "UTF-8"
- Notepad++: "Encoding" → "Convert to UTF-8"
