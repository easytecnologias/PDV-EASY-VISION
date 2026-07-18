---
name: deploy-operations
description: Deploy seguro e verificacao ponta-a-ponta do Easy Auditoria PDV (central sem git/root/docker, PDV root, cache-bust, migracao de dados). Use ao levar QUALQUER mudanca para producao.
---

# Deploy & Operations

Use esta skill sempre que for **levar uma mudanca para producao** (app.py, dashboard,
video_streamer.py) ou **migrar dados apos mudar uma regra de classificacao**. As outras
skills param no patch; esta cuida de deploy, migracao e verificacao.

## Topologia real (difere do CLAUDE.md)

- **Central `10.10.12.7`**: acesso por CHAVE (`ssh -i ~/.ssh/easy_central_ed25519 central@...`).
  `/opt/easy-auditoria-api` e `/opt/easy-auditoria-dashboard` sao `central:central`; `central`
  esta no grupo `docker`. NAO ha git no servidor; deploy e manual com backups `.bak_<ts>`.
  Containers: `easy-auditoria-api` (build de app.py), `easy-auditoria-dashboard-demo`
  (build de /opt/easy-auditoria-dashboard, portas 8098 http / 8099 https), `easy-auditoria-postgres`.
  Dashboard passa por Cloudflare (`easy-auditoria-tunnel`) que cacheia `.js`.
- **PDV `138.99.28.216:2289`** (user `rpdv`): `video_streamer.py` e `rpdv:rpdv` (scp direto),
  mas roda como **root** (servico `pdv-video-streamer.service`). `rpdv` tem sudo COM senha.
  Restart: `/self-restart` (HTTP, sem sudo) OU `sudo systemctl restart pdv-video-streamer`.

## Processo obrigatorio

### 1. Antes de deployar
- Rodar syntax-check local: `python -c "import ast; ast.parse(...)"` e `node --check`.
- Comparar repo vs servidor (eles DIVERGEM): `md5sum`, `wc -c`, versao `?v=NN`.

### 2. Deploy API (central)
`scp app.py` (backup antes) -> `ssh "cd /opt/easy-auditoria-api && docker compose up -d --build"`.
Severidade e PERSISTIDA no insert; mudanca so vale para eventos novos (ver passo 4).

### 3. Deploy dashboard (central)
- `app.js`: superset seguro, `scp` direto do repo.
- **`index.html`: NAO sobrescrever com o do repo** (repo tem versoes nunca deployadas, ~6KB a
  mais). BAIXAR o do servidor, aplicar so as edicoes (anchors do nav/section batem), devolver.
- **CACHE-BUST OBRIGATORIO**: bumpar `app.js?v=NN` no index.html. Sem isso, Cloudflare/navegador
  servem o JS VELHO da mesma URL = "nenhuma mudanca". Nao tocar `config.js` (tokens reais).
- Rebuild: `cd /opt/easy-auditoria-dashboard && docker compose up -d --build`.

### 4. Deploy PDV (video_streamer.py)
`scp` (backup `.bak_<ts>` antes) -> restart via `/self-restart` ou `sudo systemctl restart pdv-video-streamer`.

### 5. Migracao de dados (ao mudar regra de classificacao)
"Suspeito" vive em 3 fontes independentes — mudou a regra, migre as 3:
- **Central (banco)**: `docker exec -i easy-auditoria-postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'` + UPDATE.
- **PDV `/tmp/vlm_stats_<data>.json`** (root): reclassificar status dos cupons + recomputar
  contadores. `/vlm-stats` le a cada request -> reflete na hora, sem restart.
- **PDV `/opt/pdv-visual-auditor/historico_ia.json`** (contador legado, congelado): editar direto.

### 6. Verificacao ponta-a-ponta (obrigatoria)
- API: `docker exec easy-auditoria-api grep -c '<mudanca>' app.py`.
- Dashboard origin (fura Cloudflare): `curl -sk https://localhost:8099/app.js?v=NN | grep -c '<mudanca>'`
  e `curl -sk https://localhost:8099/ | grep -o 'app.js?v=[0-9]*'`.
- Banco: query de distribuicao (ex.: severidade por dia).
- PDV: `curl -s http://localhost:8765/vlm-stats?date=...&token=...`.
- Navegador do usuario: pedir `typeof <funcNova>` no Console (confirma cache).

### 7. Rollback
Restaurar o `.bak_<ts>` correspondente + `docker compose up -d --build`. Sem tocar no PDV
para mudancas so-central. Commits em branch + `git revert` do lado do repo.

## Regra de ouro
Uma mudanca so esta "pronta" quando confirmada VIVA nas 3 camadas (API, dashboard SERVIDO,
dados) — nao quando o patch foi escrito. Ver [[project-deploy-central-real]] e [[project-falsos-positivos]].
