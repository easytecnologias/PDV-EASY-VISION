---
name: ux-consistency-reviewer
description: Audita a interface (menus, botoes, rotulos, icones, acoes) procurando itens duplicados ou quase-iguais que confundem o usuario. Use ao revisar o dashboard ou antes de adicionar um item de menu/aba/botao novo.
---

# UX Consistency Reviewer 🧭

Caca na interface o que faz o usuario clicar no lugar errado: **rotulos repetidos,
itens quase-iguais, acoes ambiguas, icones duplicados, clusters confusos**. Foca em
clareza e previsibilidade, nao em estetica.

Nao existe outra skill pra isso: `consistency-auditor` cuida de regra de NEGOCIO duplicada
no codigo; esta cuida de INTERFACE.

## Quando usar
- Revisar o dashboard (`dashboard/index.html`, `dashboard/app.js`).
- **Antes de adicionar** um item de menu, aba, botao ou acao — checar se ja existe algo
  parecido que vai confundir.
- Quando o usuario relata "cliquei no errado" ou "nao sei qual abre o que".

## Processo obrigatorio
1. **Extrair todos os rotulos de nav/menu**: `grep '<span>' index.html`, `data-view=`,
   e os textos de botoes/abas. Listar todos.
2. **Contar duplicados exatos**: dois itens com o MESMO texto (ex.: dois "Auditoria IA")
   = confusao garantida. Sinalizar.
3. **Achar quase-iguais**: rotulos que compartilham palavra-chave e vivem no mesmo menu
   (ex.: "Auditoria IA" / "Erro tecnico IA" / "Historico IA" juntos) — risco de clique errado.
4. **Icones repetidos**: mesmo `data-lucide` em itens diferentes = pista visual ambigua.
5. **Acoes ambiguas**: botoes cujo texto nao diz o que acontece (ver [[artifact-design]]:
   "um controle diz exatamente o que faz").
6. **Acentuacao/consistencia de texto**: "Historico" sem acento, maiusculas inconsistentes.

## Overlap de telas / arquitetura de informacao (raiz, nao sintoma)
Rotulo/icone parecido e o SINTOMA; telas que fazem quase a mesma coisa e a RAIZ.
7. **Mapear a FONTE de dados de cada view/aba**: qual endpoint busca, qual filtro aplica.
   Grep as funcoes `iniciarView*`/`carregar*` por `apiFetch`/`/api/`/`filter`.
8. **Sinalizar redundancia**: se 2+ telas leem o MESMO endpoint e so mudam um filtro
   client-side, sao a mesma tela fragmentada em varios menus (ex.: Alertas, Auditoria IA,
   Erro tecnico IA e Ocorrencias no dashboard = todos `/api/v1/alerts?filter=all`,
   filtrados por severity). Isso confunde: o usuario nao sabe qual menu abrir.
9. **Propor consolidacao**: uma tela unica + controle de filtro/abas
   (Todos / Suspeitos / Erro tecnico / Resolvidos), no lugar de N itens de menu.
   Manter como atalho separado so o que e um fluxo de trabalho distinto (ex.: "Alertas"
   como triagem rapida do supervisor), nao cada filtro.
10. Regra: **1 dataset != N menus**. Filtro e um controle DENTRO da tela, nao um item de menu.

## Regras de nomeacao (o padrao a exigir)
- Um rotulo = uma tela. Nunca dois itens com o mesmo texto.
- Tela vs configuracao da mesma coisa: diferenciar (ex.: "Auditoria IA" vs "Ajustes da IA").
- Verbo de acao diz o resultado: "Escalar", "Confirmar alerta" (nao "Ok"/"Enviar").
- Agrupar por funcao, nao por sufixo repetido; se 3 itens dividem "IA", questionar se
  precisam de um submenu ou nomes mais distintos.

## Saida esperada
- Tabela: rotulo -> onde aparece -> tipo de problema (duplicado / quase-igual / icone / acao).
- Renomeacoes propostas (concretas), com o "por que".
- Se for um item NOVO sendo adicionado: veredito "colide com X" ou "ok, distinto".

## Regra de ouro
Se dois itens tem o mesmo nome, o usuario vai errar o clique — nao importa quao logico
seja pra quem construiu. Nomeie pela tela que abre, do ponto de vista de quem usa.
Ver [[deploy-operations]] para levar a correcao ao ar (bump de versao do dashboard!).
