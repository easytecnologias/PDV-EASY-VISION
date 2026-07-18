---
name: architecture-auditor
description: Analisa a arquitetura completa do Easy Auditoria PDV, separando responsabilidades, acoplamentos, fluxo PDV-dashboard e riscos estruturais.
---

# Architecture Auditor

## Objetivo

Entender o sistema antes de corrigir. Não escreva código antes de mapear.

## Analise

- Entradas do sistema.
- Saídas.
- APIs.
- Workers.
- Banco.
- Dashboard.
- DVR/RTSP.
- Telegram.
- Gemini/IA.
- Filas.
- Estados de auditoria.

## Sinais de problema já observados

- `app.py` grande demais.
- `dashboard/app.js` grande demais.
- `video_streamer.py` grande demais.
- Lógica de domínio misturada com transporte, UI e infraestrutura.

## Entregáveis

1. Diagrama em texto.
2. Lista de módulos atuais.
3. Lista de responsabilidades misturadas.
4. Pontos de quebra.
5. Plano de separação em PRs pequenos.

## Regra

Não proponha reescrita total. Proponha extrações pequenas e testáveis.
