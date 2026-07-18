---
name: consistency-auditor
description: Caca a MESMA regra de negocio (suspeito, severidade, status, contadores) computada em mais de um lugar com definicoes divergentes. Use antes de mudar uma regra ou quando "arrumei X e outra tela continua errada".
---

# Consistency Auditor

Use quando: (1) for **mudar uma regra de classificacao/negocio**, para saber TODOS os lugares
que precisam mudar juntos; ou (2) "arrumei X num lugar e outra tela/contador continua errado".

O bug classico deste sistema: a mesma nocao ("suspeito") era computada em 3 fontes independentes
com 3 definicoes — arrumar uma nao arrumava as outras.

## Objetivo

Garantir **uma unica fonte de verdade** por conceito de negocio, ou pelo menos que todas as
copias usem a MESMA definicao e sejam migradas juntas.

## Conceitos que costumam divergir neste projeto

- **"suspeito"**: central `severidade` (app.py) vs PDV `/vlm-stats` status de cupom
  (video_streamer.py, le `/tmp/vlm_stats`) vs `historico_ia.json` (componente legado).
- **"severidade" / "status"**: `severidade_de_acao` / `status_de_resultado` (backend) vs
  filtros client-side no dashboard (`ehSuspeitoReal`, `severity !== "ok"`).
- **"alertas" / contadores**: computados no backend (SQL), no PDV (stats) e no front (filter).
- **confianca**: fixa 85 no PDV vs exibida no dashboard.

## Processo obrigatorio

1. Escolher o conceito (ex.: "o que faz um cupom/item ser suspeito?").
2. Fazer grep do termo em TODAS as camadas: `app.py`, `dashboard/app.js`,
   `pdv_files/video_streamer.py`, `pdv_files/*`, SQL/schema, e endpoints que o dashboard
   consome (`/alerts`, `/vlm-stats`, `/stats`).
3. Para cada ocorrencia, anotar: onde NASCE, onde e PERSISTIDA, onde vira SEVERIDADE/STATUS,
   onde vira CONTADOR/EXIBICAO. Seguir o dado, nao so o nome.
4. Identificar definicoes DIVERGENTES (ex.: front exclui "info", mas PDV ainda conta divergencia).
5. Rastrear a origem dos numeros que o usuario VE (qual endpoint/fonte alimenta cada card).

## Saida esperada

- Mapa "1 conceito -> N fontes", com a definicao usada em cada uma.
- Quais divergem e como.
- Recomendacao: fonte de verdade unica OU lista de todos os pontos a mudar+migrar juntos
  (entregar essa lista para a skill `deploy-operations`, passo de migracao).
- Nunca declarar "corrigido" sem checar as N fontes que alimentam a tela.

## Regra de ouro

Se o usuario diz "nao mudou nada" depois de um fix, o numero na tela quase sempre vem de
OUTRA fonte que voce nao tocou. Ache a fonte do numero antes de mexer no codigo.

Ver [[deploy-operations]] (migracao) e [[false-positive-investigator]] (definicao de suspeito).
