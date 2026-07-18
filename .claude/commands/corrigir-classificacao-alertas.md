# Corrigir classificação de alertas

Foque apenas na classificação e contagem dos alertas.

## Tarefa

Corrija a cadeia:

`video_streamer.py` -> `/api/v1/events` em `app.py` -> banco -> `/api/v1/alerts` -> `dashboard/app.js`

Regras:

- `CONFERE` = OK/resolvido.
- `INCONCLUSIVO` = inconclusivo, não suspeito.
- `DIVERGENCIA_CATEGORIA` isolada = erro técnico/revisão leve, não suspeito real.
- `NAO_CONFERE` com evidência forte = suspeito real.
- Só contar como suspeito no card vermelho o que for `SUSPEITO_REAL` ou `critical`.

Mostre diff antes de alterar.
