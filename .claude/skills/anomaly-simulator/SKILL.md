---
name: anomaly-simulator
description: Injeta eventos SIMULADOS (roubo, erro humano, erro tecnico, casos bizarros) no Easy Auditoria PDV para testar dashboard, alertas, classificacao e o fluxo de escalar. Sempre rotulado [SIMULACAO] e removivel.
---

# Anomaly Simulator 🎭

Fabrica de anomalias para testar o sistema SEM esperar um roubo real acontecer no caixa.
Use para: validar renderizacao/contadores do dashboard, testar a aba "Erro tecnico IA" e o
botao Escalar, ensaiar demos, checar severidade/status, e stress-test de casos estranhos.

## ⚠️ Regras de seguranca (OBRIGATORIAS)

Isto injeta em PRODUCAO com supervisor real olhando. SEMPRE:
1. Prefixar `produto` com `[SIMULACAO]` e usar `cupom` com prefixo `SIM-`.
2. `imagem` UNICA por evento (`sim_<cenario>_<n>.jpg`) — respeita `UNIQUE(loja_id,timestamp,pdv,imagem)` e permite deletar.
3. `raw_json` com `{"simulacao": true, ...}`.
4. **Limpar depois** (comando no fim). Nunca deixar simulacao dormindo no banco.

## ⏰ Pegadinha do timezone (CRITICO)
O Postgres roda em **UTC**, mas PDV/dashboard filtram por data **LOCAL** (America/Sao_Paulo, -03).
`to_char(now(),...)` gera data UTC e o evento cai no dia ERRADO (some do "Hoje"). SEMPRE usar:
`to_char(now() AT TIME ZONE 'America/Sao_Paulo','YYYY-MM-DD HH24:MI:SS')`.
Para "item teleportado"/"futuro", ajustar o intervalo APOS o AT TIME ZONE.

## Como injetar (via banco, central)

`ssh -i ~/.ssh/easy_central_ed25519 central@10.10.12.7` +
`docker exec -i easy-auditoria-postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'` + SQL.
Colunas: loja_id, timestamp (TEXT 'YYYY-MM-DD HH24:MI:SS'), pdv, cupom,
imagem, produto, valor, quantidade, modo, resultado, confianca, comparacao_pdv,
possivel_divergencia, acao_recomendada, severidade, status, raw_json.

**Mapa de gravidade** (o que o dashboard mostra): `acao_recomendada='revisar cupom'`->`severidade='critical'`;
`='liberar'`->`'ok'`; `='revisar'`->`'info'` (erro tecnico); outro->`'warning'`. `status='pending'` = a revisar.

## Catalogo criativo de cenarios

### 🔴 Fraude (roubo)
- **Troca de etiqueta**: registra chiclete R$0,50, camera ve whisky R$189,90. `NAO_CONFERE`, `revisar cupom`, conf 96.
- **Sweethearting** (nao escaneou): item vai pra sacola sem bipar. produto "[SIMULACAO] Fralda passou sem registro", `NAO_CONFERE`, `revisar cupom`.
- **Banana trick**: item caro pesado como barato. "[SIMULACAO] Picanha registrada como banana".
- **Cancelamento fantasma**: finge cancelar e leva. modo 'video', `possivel_divergencia`='item saiu apos cancelamento'.

### 🟡 Erro humano
- **Duplo scan**: mesmo item 2x (cliente pagou dobrado). `DIVERGENCIA_CATEGORIA`? nao — use `NAO_CONFERE` leve, `revisar`.
- **Quantidade errada**: registrou 1, levou 3. comparacao 'PDV qtd=1 | visual qtd=3'.
- **Categoria trocada sem ma fe**: `DIVERGENCIA_CATEGORIA`, `revisar` -> vira `info` (testa a aba Erro tecnico).

### 🛠️ Erro tecnico / IA
- **Produto fantasma**: camera ve item anterior ainda na esteira. `INCONCLUSIVO`, conf 30.
- **Sem footage**: `NAO_ANALISADO`, comparacao 'Sem frame do DVR na janela'.

### 🤪 Bizarro (stress-test — o sistema aguenta?)
- **Alucinacao do Gemini**: produto "[SIMULACAO] Unicornio de pelucia tamanho real", conf 99.
- **Velocidade impossivel**: 50 itens no mesmo timestamp (loop de INSERT).
- **Item teleportado**: aparece na sacola, timestamp ANTES do cupom abrir.
- **Valor negativo / gigante**: valor -50 ou 999999.99 (testa formatacao do dashboard).
- **Schrodinger**: dois eventos mesmo produto, um `severidade='ok'` outro `'critical'` (testa consistencia — ver [[consistency-auditor]]).
- **Timestamp do futuro**: `to_char(now()+interval '2 hours',...)` (DVR drift extremo).

## Verificacao
Dashboard F5 -> Alertas recentes / contador de criticos. Ou query:
`SELECT id, produto, severidade, status FROM auditoria_eventos WHERE cupom LIKE 'SIM-%';`

## 🧹 Limpeza (rodar SEMPRE ao terminar)
`DELETE FROM auditoria_eventos WHERE cupom LIKE 'SIM-%' OR imagem LIKE 'sim_%' OR raw_json LIKE '%"simulacao": true%';`

Deploy/verificacao ponta-a-ponta: [[deploy-operations]].
