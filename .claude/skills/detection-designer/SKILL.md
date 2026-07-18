---
name: detection-designer
description: Desenha COMO detectar um vetor de fraude que hoje e ponto cego, usando o que o sistema JA tem (spy file VIT, DVR continuo, ROI, Gemini). Transforma "o sistema nao pega X" em uma spec buildavel (gatilho + sinal + integracao).
---

# Detection Designer 🛠️

Pega um ponto cego apontado pela [[fraud-coverage-auditor]] e desenha uma **deteccao concreta
e buildavel** — sem fantasia de hardware novo. Usa so a infra atual.

## Infra disponivel (o material de trabalho)
- **Spy file**: por cupom, os VITs = itens registrados (descricao, quantidade, valor, timestamp).
  Ou seja: **contagem e valor REGISTRADOS** sao conhecidos.
- **DVR iMHDX (192.168.24.227)**: video **CONTINUO** (nao so no bip). ffmpeg extrai frames arbitrarios.
- **ROI ja calibrado** da zona do scanner + calibracao de offset DVR<->PDV.
- **Gemini Vision** (frames) e possibilidade de tracking/contagem de objetos em video.

## Principio central: mudar de "verificar bip" para "reconciliar realidade"
O pipeline atual so age NO bip. A maioria dos pontos cegos se resolve **olhando o intervalo
INTEIRO do cupom** (ABRECUPOM->FECHACUPOM) no video continuo, e comparando com os VITs.

## Processo obrigatorio
Para o vetor escolhido, produzir uma spec com 5 campos:

1. **GATILHO** — quando rodar (ex.: em FECHACUPOM, varrer o video do cupom inteiro, nao so bips).
2. **SINAL** — o que medir no video (ex.: contar objetos distintos que cruzam a ROI do scanner).
3. **RECONCILIACAO** — comparar com o dado do spy (ex.: objetos_fisicos vs count(VIT)).
4. **REGRA DE ALERTA** — quando vira suspeito (ex.: fisico > registrado + margem => item sem bip).
5. **INTEGRACAO** — onde encaixa (novo endpoint no video_streamer, novo resultado, severidade,
   como o dashboard/erro-tecnico exibe) e o custo (chamadas Gemini, ffmpeg, latencia).

## Blueprints por vetor (ponto de partida)
- **Sweethearting / passar sem bipar** → contar objetos que cruzam a ROI do scanner no intervalo
  do cupom (frames continuos) e comparar com count(VIT). fisico > registrado => alerta forte.
- **Fraude de quantidade** → mesma contagem, por janela de tempo do item.
- **Item escondido / zona de saida** → definir 2a ROI (sacola/saida); objeto que chega la sem
  ter passado pela ROI do scanner.
- **Cancelamento fantasma** → cruzar evento CANCELA do spy com "item continuou o trajeto no video".

## Saida esperada
- Spec dos 5 campos para o vetor.
- Prova de viabilidade com a infra atual (o que ja existe vs o que falta implementar).
- Estimativa de custo/latencia (frames continuos e mais caro que 1 frame no bip).
- Riscos de falso positivo e como calibrar (a lição de [[false-positive-investigator]]:
  exigir evidencia forte antes de marcar suspeito real).
- Plano de PRs pequenos (handoff [[auto-refactor-planner]]) e deploy ([[deploy-operations]]).
- Testar com [[anomaly-simulator]] antes e depois.

## Regra de ouro
Nao proponha detector que dependa de hardware/dado que o sistema nao tem. Se cabe no
"video continuo + VITs do spy", e buildavel hoje. Comece SEMPRE pela reconciliacao de contagem
(fisico x registrado) — e o maior ganho com a menor mudanca de arquitetura.

## Licao de calibracao (medido 2026-07-07, detector de sweethearting em shadow)
O paradigma (reconciliacao) esta certo, MAS "1 chamada de LLM contando objetos num clip" e
RUIDOSO demais: deltas medidos foram +2, +9, -2 em cupons vizinhos (Gemini conta maos,
itens remanuseados, sacola, fundo). Ligar isso = repetir o desastre de falso positivo.
Aprendizados obrigatorios ao desenhar contagem:
1. LLM contando video != rastreamento de objeto. Para contagem confiavel, usar
   deteccao/tracking frame-a-frame (cruzou a linha da ROI?), nao pedir um numero ao LLM.
2. **Itens por peso (kg)** quebram `registrados`: `Quant` e PESO, nao nº de objetos.
   Contar VITs/gestos de scan, e tratar itens por peso a parte.
3. Clips longos (cupom grande) dao timeout no upload — janela por item, nao cupom inteiro.
4. SEMPRE shadow mode primeiro: medir a distribuicao do delta antes de alertar. Se o delta
   varia muito em cupons normais, o SINAL nao presta ainda — nao e fraude.
