---
name: code-simplifier
description: Encontra código morto, duplicação, funções gigantes e separa responsabilidades sem reescrever tudo.
---

# Code Simplifier

## Objetivo

Reduzir complexidade com segurança.

## Faça

- Liste arquivos grandes.
- Liste funções grandes.
- Liste duplicações.
- Liste código morto.
- Proponha extrações pequenas.

## Ordem recomendada

1. Extrair labels/status/severidade para módulo de domínio.
2. Extrair cliente API do streamer.
3. Extrair renderização do dashboard em módulos.
4. Só depois mexer na arquitetura maior.
