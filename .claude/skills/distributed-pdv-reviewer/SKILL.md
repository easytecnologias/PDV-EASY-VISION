---
name: distributed-pdv-reviewer
description: Revisa a arquitetura distribuída onde cada PDV é seu próprio servidor e envia dados ao dashboard central.
---

# Distributed PDV Reviewer

## Objetivo

Garantir que cada PDV possa operar localmente, tolerar falhas e sincronizar com dashboard sem duplicar ou perder eventos.

## Verifique

- Tokens/API por loja e PDV.
- Reenvio em falha de rede.
- Duplicidade de eventos.
- Chave de idempotência.
- Relógio/offset entre PDV, DVR e dashboard.
- Fila local.
- Persistência antes de enviar.
- Health check.
- Atualização do dashboard.

## Recomendação principal

Todo evento deve ter `event_id` determinístico:

```text
loja + pdv + cupom + timestamp + produto + sequencia
```

Não dependa apenas de timestamp/imagem para deduplicar.
