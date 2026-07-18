---
name: auto-refactor-planner
description: Transforma achados de auditoria em sequência de PRs pequenos, reversíveis e testáveis.
---

# Auto Refactor Planner

## Objetivo

Criar plano de correção que o Claude Code consiga executar sem destruir o sistema.

## Formato obrigatório

Para cada PR:

- Nome.
- Objetivo.
- Arquivos tocados.
- Mudança mínima.
- Risco.
- Como testar.
- Como reverter.

## Ordem sugerida para este projeto

1. Corrigir classificação de `DIVERGENCIA_CATEGORIA`.
2. Ajustar contadores do dashboard.
3. Criar score de risco.
4. Separar erro técnico de suspeito real.
5. Adicionar relatório por cupom.
6. Extrair módulo de domínio.
7. Extrair cliente de API do PDV.
8. Criar testes.
