---
name: audit-result-auditor
description: Audita o AUDITOR — dentro da Auditoria IA, pega vereditos "Aprovado" (CONFERE) cujo texto da IA NAO bate com o produto registrado (falso negativo / aprovacao carimbada). Use quando "tem coisa aprovada que o texto nao confere".
---

# Audit Result Auditor 🔎

Verifica se as APROVACOES sao confiaveis. A `false-positive-investigator` cuida de suspeito
demais; esta cuida do lado oposto: **"Aprovado" onde a evidencia nao sustenta o match**.

Conecta com a causa raiz ja mapeada ([[project-deteccao-gaps]]): se a camera as vezes ve o
frame errado, alguns "Aprovado" tambem estao errados — a IA viu um item parecido e carimbou.

## Objetivo
Achar vereditos onde o TEXTO da IA nao confirma o PRODUTO registrado, mesmo marcado Aprovado.

## Fonte de dados (central)
`auditoria_eventos` (via `docker exec easy-auditoria-postgres` + psql). Campos chave:
`resultado` (CONFERE/CONFERE_POR_REGRA_DE_VALOR/...), `produto` (registrado),
`comparacao_pdv` / `possivel_divergencia` / `raw_json` (o texto/analise do Gemini), `confianca`.

## Processo obrigatorio
1. Selecionar os **aprovados**: `resultado LIKE 'CONFERE%'` do periodo.
2. Para cada um, extrair o que a IA **descreveu** (limpar o "PASSO N:" do prompt) e comparar
   com o `produto` registrado.
3. Classificar cada aprovacao:
   - **OK**: a descricao confirma o produto (mesmo tipo/categoria).
   - **GENERICO**: texto vago ("um objeto", "um pacote") — aprovou sem confirmar de fato.
   - **NAO IDENTIFICADO**: "nao da pra ver / sem produto" mas aprovou mesmo assim
     (o proprio prompt diz "nunca responda OK se nao viu produto" — violacao).
   - **CONFLITO**: a descricao e claramente OUTRO produto (ex.: registrado "Detergente",
     texto "uma garrafa de refrigerante") = **falso negativo**.
4. Usar um **juiz LLM** para o match semantico produto x descricao (batem? sim/generico/nao),
   nao string-match ingenuo (produto por categoria).
5. Medir a taxa: quantos % dos "Aprovado" sao CONFLITO/NAO IDENTIFICADO (aprovacao nao confiavel).

## Saida esperada
- Tabela: produto registrado | o que a IA viu | veredito | classe (OK/GENERICO/NAO ID/CONFLITO).
- Taxa de aprovacao nao confiavel.
- Ligar com a causa raiz: se muitos CONFLITO, e o mesmo problema de frame errado
  ([[project-deteccao-gaps]]) — nao adianta so re-classificar, precisa da camera certa.

## Regra de ouro
Aprovacao so vale se o texto CONFIRMA o produto especifico. "Parece um produto qualquer",
"generico" ou "nao identifiquei" NAO e confirmacao — e aprovacao carimbada, tao ruim quanto
suspeito falso. Auditar o auditor faz parte de confiar no numero.
