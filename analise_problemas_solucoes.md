# Análise de Problemas e Soluções - IntegraGAL

## Problemas Identificados

### Problema 1: Dados incorretos nos campos
**Sintoma**: Config.json correto, mas campos mostram valores errados
**Causa raiz**: Campos duplicados no código lendo chaves inexistentes

### Problema 2: Janela não fecha
**Sintoma**: Terminal reporta fechamento, mas janela continua visível
**Causa raiz**: Conflitos entre métodos de fechamento e flags inconsistentes

## Soluções Propostas

### A) Rápida (10 min) - Correção mínima
- Dificuldade: ⭐⭐
- Probabilidade: 90%

### B) Robusta (25 min) - Refatoração completa  
- Dificuldade: ⭐⭐⭐⭐
- Probabilidade: 99%

### C) Disruptiva (40 min) - Arquitetura nova
- Dificuldade: ⭐⭐⭐⭐⭐
- Probabilidade: 95%