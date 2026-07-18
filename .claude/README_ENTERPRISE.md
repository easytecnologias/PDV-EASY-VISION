# Easy PDV Auditoria — Claude Enterprise Skills

Pacote de skills para o Claude Code analisar e corrigir o sistema Easy Auditoria PDV com foco em arquitetura, falsos positivos, IA, segurança, performance e refatoração segura.

## Como instalar

Copie a pasta `.claude` e o arquivo `CLAUDE.md` para a raiz do projeto `easy-pdv-auditoria-main`.

```bash
cp -r .claude CLAUDE.md /caminho/do/easy-pdv-auditoria-main/
```

Depois abra o Claude Code na raiz do projeto e use:

```text
/auditoria-enterprise
```

Para atacar diretamente os falsos positivos:

```text
/reduzir-falsos-positivos
```

Para criar correções pequenas e seguras:

```text
/plano-refatoracao-segura
```

## O que este pacote faz

- Mapeia a arquitetura inteira.
- Investiga por que o dashboard está mostrando excesso de suspeitos.
- Separa erro técnico, inconclusivo, divergência fraca e suspeita real.
- Obriga auditoria por cupom, não apenas por item isolado.
- Cria score de risco antes de marcar como suspeito.
- Gera plano de refatoração em PRs pequenos.
- Evita quebrar produção.

## Arquivos importantes detectados no projeto atual

- `app.py`: API FastAPI, eventos, status, severidade e persistência.
- `dashboard/app.js`: dashboard grande com lógica de UI, pipeline e alertas.
- `pdv_files/video_streamer.py`: captura, auditoria Gemini, envio de eventos.
- `pdv_files/pdv_telegram_assistant.py`: análise/assistente Telegram.
- `schema_pg.sql`: tabelas principais.
- `docker-compose.yml`: infraestrutura local.
