---
name: security-reviewer
description: Revisa segurança de API, tokens, upload, CORS, SSL, autenticação e exposição do sistema Easy Auditoria PDV.
---

# Security Reviewer

## Verifique com prioridade

- Tokens em query string.
- CORS aberto.
- SSL verification desabilitado.
- Upload/path traversal.
- Credenciais em logs.
- Endpoints de delete/reset sem proteção forte.
- Permissões por loja.
- Exposição do dashboard em IP privado/público.

## Regra

Não quebre operação em campo. Sugira migração segura.
