---
name: frontend-design-reviewer
description: Revisa uma TELA existente do dashboard (nao artifact novo) por elegancia e performance percebida — vazamento de dados internos, truncamento, hierarquia, cor com significado, densidade, e render lento. Use quando uma pagina parece "esquisita" ou "lenta".
---

# Frontend Design Reviewer 🎨

Deixa uma tela EXISTENTE do dashboard elegante e rapida. Complementa a `ux-consistency-reviewer`
(menus/rotulos) e usa os principios de `artifact-design`, mas aplicados a paginas ja em producao.

## Quando usar
- Uma pagina parece "esquisita", "poluida", "amadora" ou "lenta".
- Antes de mostrar uma tela pro cliente.

## Checklist de ELEGANCIA (o que procurar)
1. **Vazamento de dado interno**: texto cru do modelo/prompt na UI (ex.: "sim PASSO 2:" do
   prompt do Gemini aparecendo na coluna). Limpar/formatar antes de exibir, nunca mostrar cru.
2. **Truncamento de cabecalho/celula**: `table-layout:fixed` + width estreita + `text-overflow`
   corta rotulos ("RESULT...", "PRODUTO RE..."). Encurtar o rotulo OU ajustar a largura.
3. **Cor sem significado**: barra/badge sempre da mesma cor (ex.: confianca sempre vermelha)
   nao informa. Colorir por estado (ok=verde, erro tecnico=ambar, suspeito=vermelho).
4. **Estado sem cor**: severidade/estado novo sem regra CSS (ex.: `.severity.info` sem `background`
   -> bolinha invisivel). Todo estado precisa de sinal visual.
5. **Densidade/hierarquia**: muita coluna, thumbnail minusculo, tudo no mesmo peso. Dar respiro,
   destacar o que importa.
6. **Estados de loading/empty**: lista sem esqueleto/placeholder; vazio sem mensagem util.

## Checklist de PERFORMANCE PERCEBIDA
7. **Render de lista gigante**: montar centenas de `<tr>` de uma vez trava. Limitar
   (ex.: `MAX_LINHAS = 100` + "mostrando 100 de N") ou paginar/virtualizar.
8. **Re-render por tecla**: busca que chama render a cada keystroke reconstroi tudo.
   **Debounce** (~200ms).
9. **Trabalho global desnecessario por render**: `lucide.createIcons()` / querys no documento
   inteiro a cada render. Escopar ou reduzir o volume (menos linhas = menos icones).
10. **N requisicoes de imagem**: N miniaturas remotas de uma vez. `loading="lazy"` + limitar linhas.

## Saida esperada
- Lista dos problemas (elegancia + perf), cada um com o trecho/arquivo.
- Correcoes concretas e minimas (dashboard/app.js, index.html, styles.css).
- Lembrar do cache-bust: bumpar `app.js?v=` E `styles.css?v=` ao mexer nesses arquivos.

## Regra de ouro
A tela mostra o que o usuario reconhece, nao como o sistema pensa. Nada de prompt cru, nada de
cor decorativa: cor = estado. E lista longa se limita ou pagina — nunca joga 200 linhas na cara.
Levar ao ar: [[deploy-operations]] (bump de versao de JS **e** CSS).
