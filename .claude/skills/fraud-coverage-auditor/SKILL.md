---
name: fraud-coverage-auditor
description: Mapeia quais vetores de fraude/erro o sistema DETECTA de verdade vs os pontos cegos, e por que. Use quando alguem pergunta "o sistema pega roubo X?" ou para avaliar o valor real de deteccao antes de prometer algo.
---

# Fraud Coverage Auditor 🎯

Responde a pergunta que mais importa: **"quais roubos/erros o sistema REALMENTE pega hoje, e
quais sao pontos cegos?"** — separando o que a IA *poderia* dizer do que a arquitetura
*permite* detectar.

Regra dura deste sistema: ele e um **verificador de escaneamento** (gatilho por VIT/bip),
NAO um detector de roubo. So "ve" quando ha um item registrado. Ver [[project-deteccao-gaps]].

## Quando usar
- "O sistema detecta [passar sem bipar / item na sacola / quantidade errada]?"
- Antes de demo/proposta comercial (nao prometer o que a arquitetura nao entrega).
- Depois de mexer em classificacao, para reavaliar o valor de deteccao restante.
- Quando um alerta SIMULADO ([[anomaly-simulator]]) da a falsa impressao de capacidade.

## Processo obrigatorio

1. **Liste os vetores** (fraude do operador, erro humano, erro tecnico). Base:
   sweethearting/passar-sem-bipar, troca de etiqueta, banana trick, cancelamento fantasma,
   duplo scan, quantidade divergente, item escondido, devolucao fantasma.
2. **Para cada vetor, ache o GATILHO no codigo**: existe evento no spy file (VIT, FECHACUPOM,
   CANCELA) que dispara a analise? Se o vetor NAO gera bip/VIT, o sistema e cego (sem gatilho).
3. **Para cada vetor com gatilho, ache o SINAL**: o que a IA compara? (produto visto x
   produto registrado). Isso so pega *categoria trocada*, nao *ausencia* nem *contagem*.
4. **Classifique**: DETECTA / PARCIAL / CEGO — e escreva o PORQUE arquitetural.
5. **Avalie a qualidade do sinal**: o sinal detectado e ruido (falso positivo) ou evidencia
   forte? (ex.: divergencia de categoria isolada = ruido — ver [[false-positive-investigator]]).

## Saida esperada
- Tabela: vetor -> DETECTA/PARCIAL/CEGO -> gatilho -> sinal -> por que.
- "Placar honesto": de N vetores, quantos sao detectados de verdade.
- Ponto cego #1 nomeado explicitamente (hoje: sweethearting).
- NAO deixar impressao de capacidade que a arquitetura nao tem. Se um alerta veio de
  simulacao/insercao manual, dizer que NAO prova deteccao.
- Handoff: para FECHAR um gap, chamar [[detection-designer]].

## Regra de ouro
"O que a IA escreve num alerta" != "o que o sistema consegue detectar". So conta como
deteccao real se existe um GATILHO + SINAL no pipeline. Sem gatilho, o roubo e invisivel —
por mais esperto que seja o prompt.
