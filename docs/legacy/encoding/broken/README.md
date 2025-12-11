# Scripts com SyntaxError - Quarentena

Estes arquivos foram movidos para cá porque contêm erros de sintaxe Python que impedem a compilação do projeto.

## Arquivos:

1. **corrigir_encoding_final.py** - Emoji quebrado na linha 76
2. **fix_mojibake_comprehensive.py** - Dicionário malformado (linhas 76-78)
3. **fix_mojibake_project.py** - String solta não comentada

## Problema:

Todos estes scripts foram criados para corrigir problemas de mojibake/encoding, mas eles mesmos contêm caracteres UTF-8 corrompidos que causam `SyntaxError` ao compilar.

## Status:

❌ **NÃO USAR** - Arquivos quebrados  
⚠️ **MANTER APENAS COMO REFERÊNCIA HISTÓRICA**

## Ação recomendada:

- Se precisar de funcionalidade similar, reescrever do zero
- Usar `fix_mojibake.py` (na raiz) que está funcionando
- Ou deletar completamente se não houver mais necessidade

---

**Data da quarentena:** 10/12/2025  
**Motivo:** Correção de SyntaxErrors identificados por `compileall`  
**Ref:** Análise externa - Bug #20
