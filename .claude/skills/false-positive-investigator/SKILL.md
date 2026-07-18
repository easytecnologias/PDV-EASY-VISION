---
name: false-positive-investigator
description: Investiga e reduz falsos positivos no Easy Auditoria PDV, especialmente Categoria divergente, suspeitos excessivos e contadores errados no dashboard.
---

# False Positive Investigator

Use esta skill quando houver muitos alertas suspeitos, divergência de categoria, IA acusando demais ou dashboard com taxa de suspeitos alta.

## Objetivo

Reduzir falsos positivos sem esconder suspeitas reais.

## Arquivos prioritários

1. `pdv_files/video_streamer.py`
2. `app.py`
3. `dashboard/app.js`
4. `schema_pg.sql`
5. `pdv_files/pdv_telegram_assistant.py`

## Processo obrigatório

1. Localize onde nasce o resultado da IA.
2. Localize onde `sus=True` vira `DIVERGENCIA_CATEGORIA`.
3. Localize onde `DIVERGENCIA_CATEGORIA` vira `acao_recomendada`.
4. Localize onde o backend transforma isso em `severidade` e `status`.
5. Localize onde o dashboard soma suspeitos.
6. Proponha patch pequeno.
7. Crie teste manual ou automatizado.

## Hipóteses fortes neste projeto

- `DIVERGENCIA_CATEGORIA` está sendo contado como suspeito forte.
- A confiança está fixa em `85` quando não é inconclusivo.
- A ação `revisar` vira severidade `warning` e aparece como alerta.
- O dashboard pode considerar tudo que não é `ok` como suspeito.
- A auditoria por item está pesando mais do que o cupom completo.

## Regras novas recomendadas

### Categoria divergente isolada

Não deve ser suspeito real.

Use:

```python
if resultado == "DIVERGENCIA_CATEGORIA" and not evidencias_fortes:
    resultado = "INCONCLUSIVO"
    acao_recomendada = "erro tecnico ia"
    severidade = "info"
```

### Score de risco

Crie pontuação antes de suspeitar:

- categoria divergente: +10
- baixa qualidade/oclusão: -20
- produto não passou no scanner: +40
- produto foi para sacola sem registro: +50
- quantidade divergente: +35
- valor alto: +10 a +30
- cupom com total visual compatível: -30

Classificação:

- 0–39: ignorar/erro técnico
- 40–69: revisão leve
- 70+: suspeito real

## Saída esperada

Entregue:

- mapa do fluxo do falso positivo;
- linhas/trechos envolvidos;
- patch mínimo;
- impacto esperado;
- teste de validação.
