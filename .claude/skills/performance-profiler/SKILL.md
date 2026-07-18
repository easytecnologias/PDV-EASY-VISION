---
name: performance-profiler
description: Procura gargalos de CPU, memória, rede, banco, Gemini e dashboard no Easy Auditoria PDV.
---

# Performance Profiler

## Verifique

- Chamadas Gemini por item.
- Reprocessamento de cupom.
- Loops no dashboard.
- Tamanho de `app.js` e renderização.
- Consultas SQL sem índice.
- Upload/download de snapshots.
- Uso de threads.
- Fila e locks.

## Saída

- Top 10 gargalos prováveis.
- Métrica para medir cada um.
- Patch pequeno para cada gargalo.
