# Contexto obrigatório do projeto Easy Auditoria PDV

Você está trabalhando em um sistema de auditoria de supermercado/PDV.

## Objetivo do produto

Cada PDV é um servidor local que captura eventos, cupom/log do caixa, imagens/vídeo do DVR/RTSP e envia resultados para um dashboard central. O objetivo é reduzir perdas e fraudes sem inundar o supervisor com falsos positivos.

## Problema principal atual

O dashboard está marcando suspeitos demais. Exemplo real observado:

- 97 cupons auditados.
- 19 OK.
- 72 suspeitos.
- Muitos alertas são `Categoria divergente` com confiança 85%.

Isso indica sistema agressivo, não necessariamente fraude real.

## Regra de ouro

Nunca transforme divergência visual fraca em suspeita real sem evidência temporal/comportamental.

`DIVERGENCIA_CATEGORIA` isolada deve ser `INCONCLUSIVO` ou `ERRO_TECNICO_IA`, não fraude.

## Conceitos de domínio

- PDV: caixa/local onde roda o worker.
- Cupom: compra fechada, contendo vários itens.
- Item: produto registrado no cupom.
- Scanner: região/evento onde o produto deveria passar.
- Sacola/saída: região onde produto vai após registro.
- Evidência temporal: produto entrou, passou no scanner, saiu, cupom registrou.
- Suspeito real: comportamento com evidência forte, não apenas erro de categoria.

## Arquivos críticos

- `app.py`
  - Recebe eventos em `/api/v1/events`.
  - Calcula severidade por `acao_recomendada`.
  - Calcula status por `resultado`.
  - Mapeia labels de eventos.

- `pdv_files/video_streamer.py`
  - Chama Gemini/IA.
  - Atualmente converte `sus=True` em `DIVERGENCIA_CATEGORIA`.
  - Envia `confianca=85` para divergência, o que pode inflar falsos positivos.
  - `_postar_evento_fisico` define `acao = "revisar"` para divergência.

- `dashboard/app.js`
  - Mostra pipeline.
  - Soma suspeitos e calcula percentuais.
  - Pode estar classificando `severity !== ok` como suspeito.

## Princípio de correção

Antes de alterar código:

1. Mapear onde o resultado nasce.
2. Mapear onde ele é persistido.
3. Mapear onde vira severidade/status.
4. Mapear onde vira contador no dashboard.
5. Criar teste/reprodução.
6. Corrigir em menor patch possível.
7. Não refatorar tudo de uma vez.

## Política de falsos positivos

Use classificação em camadas:

- `OK`: evidência suficiente de compatibilidade.
- `INCONCLUSIVO`: imagem ruim, oclusão, baixa confiança, produto genérico.
- `ERRO_TECNICO_IA`: categoria divergente isolada, baixa qualidade, modelo não conseguiu diferenciar.
- `REVISAO_LEVE`: divergência fraca com algum sinal secundário.
- `SUSPEITO_REAL`: evidência temporal ou operacional forte.
- `CRITICO`: item não registrado, item na sacola sem passagem, diferença de quantidade/valor relevante, cancelamento/estorno suspeito.

## O que não fazer

- Não marcar `DIVERGENCIA_CATEGORIA` isolada como suspeito real.
- Não usar confiança fixa 85 para todos os alertas.
- Não contar inconclusivo como suspeito no dashboard.
- Não misturar erro técnico com fraude.
- Não reescrever `app.py` inteiro em uma única mudança.
- Não alterar Docker/infra junto com regra de negócio no mesmo patch.

## Meta de produto

Em uma operação normal, a tela deve priorizar poucos casos com evidência forte. Exemplo desejável:

- 97 auditados.
- 70 OK.
- 15 inconclusivos/erro técnico.
- 8 revisão leve.
- 4 suspeitos reais.
