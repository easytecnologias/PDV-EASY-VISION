# Reduzir falsos positivos

Use a skill `false-positive-investigator` e `ai-pipeline-reviewer`.

## Objetivo

Reduzir excesso de suspeitos sem esconder fraude real.

## Tarefa

1. Investigue `DIVERGENCIA_CATEGORIA` em `video_streamer.py`, `app.py` e `dashboard/app.js`.
2. Mostre exatamente onde o falso positivo nasce.
3. Crie um patch pequeno para:
   - não contar categoria divergente isolada como suspeito real;
   - separar `INCONCLUSIVO`, `ERRO_TECNICO_IA`, `REVISAO_LEVE`, `SUSPEITO_REAL`;
   - remover confiança fixa 85 quando não houver evidência forte;
   - ajustar dashboard para não somar inconclusivos/erro técnico como suspeitos.
4. Antes de aplicar, mostre o diff planejado.
5. Aplique apenas se o patch for pequeno e reversível.
6. Crie ou descreva teste manual.
