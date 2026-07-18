---
name: dvr-time-sync-fixer
description: Diagnostica e conserta a sincronizacao de relogio DVR/PDV e os horarios dos frames (offset, auto-correcao de relogio quebrando frames, menu Manutencao quebrado por mixed content). Use quando "os frames estao com hora errada" ou "o sync de hora quebrou".
---

# DVR Time Sync Fixer ⏱️

Conserta os horarios dos frames e a sincronizacao DVR/PDV. O frame certo depende do
alinhamento entre o relogio do DVR e o do PDV; quando isso quebra, o Gemini analisa o
frame do momento errado (ligado a [[project-deteccao-gaps]]).

## Como o sistema funciona (video_streamer.py)
- **Offset por software** (a rede de seguranca): `_calibrate_dvr_offset()` mede DVR-PDV
  (ponto medio do roundtrip), `_get_dvr_offset()` devolve. A captura de frame soma o offset
  (`ts_dvr = ts + offset - 1`). Recalibra fresco no inicio de cada `_gemini_analyze_cupom`.
- **Reescrita do relogio do DVR** (opcional e PERIGOSA): `_dvr_calibration_loop()` a cada 3 min,
  se `abs(offset) >= 1`, chama `_set_dvr_clock()` que faz **duplo-salto** (+30s, depois corrige)
  pra furar o threshold do firmware.
- **Endpoints**: `/dvr-offset` (le estado), `/dvr-sync` (forca sync manual).
- **Menu Manutencao** (dashboard): le `/dvr-offset` a cada 10s, botao chama `/dvr-sync`.

## Modos de falha conhecidos (checar todos)
1. **Duplo-salto deixa o DVR +30s**: se o 2o SET falha (rede), o DVR fica +30s a frente.
   O loop **nao checa o retorno de `_set_dvr_clock`** -> falha silenciosa -> TODOS os frames
   30s errados. Sintoma: offset pula pra ~+30s e nao volta; Gemini ve item vizinho.
2. **Auto-correcao agressiva demais** (`>=1s`): reescreve o hardware a cada 3 min a toa,
   sendo que o **offset por software ja compensa**. Cada reescrita tem uma janela de risco.
3. **Menu Manutencao quebrado = MIXED CONTENT**: o dashboard e HTTPS, o streamer e HTTP.
   Chamadas com URL ABSOLUTA `${STREAMER}/dvr-offset` (`http://ip:8765`) sao bloqueadas pelo
   navegador. As que funcionam usam a RELATIVA `/streamer/...` (proxy nginx HTTPS->HTTP que ja existe).

## Diagnostico (na ordem)
1. `curl .../streamer/dvr-offset?token=...` -> ver `offset_seconds` e `last_calibration`.
   Offset preso em ~+30s = falha do duplo-salto (modo 1).
2. Comparar relogio do DVR (`getCurrentTime` CGI) com o do PDV (`date`).
3. Logs do streamer: `grep 'dvr-clock\|dvr-calibrate\|corrigindo relogio'` -> ver SET falhando/repetindo.
4. Console do navegador na Manutencao: erro de **Mixed Content** = modo 3.
5. Validar um frame de hora conhecida: bate com o item registrado?

## Principios de correcao
- **Frames**: confie no **offset por software** (fresco por cupom). Nao dependa do relogio do
  hardware estar perfeito. Essa e a rede de seguranca — ela sozinha ja resolve o timing.
- **Reescrita do relogio**: tornar conservadora (limite `>=3s`, nao `>=1s`), **CHECAR o retorno**
  de `_set_dvr_clock`, **verificar depois** (re-medir) e NUNCA deixar pior/+30s; ou tornar
  **manual apenas** (botao da Manutencao) e desligar o loop automatico.
- **Menu Manutencao / qualquer chamada navegador->streamer**: usar a relativa `/streamer/...`
  (proxy HTTPS), nunca a absoluta `http://ip:8765` (mixed content).

## Saida esperada
- Qual dos 3 modos esta ativo (com evidencia: offset, logs, console).
- Patch minimo por modo. Lembrar: fix de PDV precisa redeploy do video_streamer
  ([[deploy-operations]]); fix do menu e so dashboard (bump de versao).

## Regra de ouro
O offset por software e a verdade; o relogio do hardware e conveniencia. Se for corrigir o
hardware, verifique que melhorou — corrigir as cegas (duplo-salto sem checagem) quebra mais
do que conserta. E navegador->streamer sempre pelo proxy same-origin.
