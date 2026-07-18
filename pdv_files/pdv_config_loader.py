#!/usr/bin/env python3
"""Carrega configuração remota da API Easy Auditoria com cache local.

Usado pelos serviços do PDV (worker, auditor, sync) para ler as configurações
salvas no dashboard sem depender de restart do systemd para cada mudança.
Cache em memória (5 min) + fallback em disco se a API estiver fora.
"""
import json
import os
import time
from pathlib import Path

_CACHE_PATH = Path("/var/lib/pdv-visual-auditor/remote_config.json")
_CACHE_TTL = 300.0  # 5 minutos

_memory_cache: dict = {}
_memory_ts: float = 0.0


def fetch(force: bool = False) -> dict:
    """Retorna a configuração remota mesclada (loja + PDV).

    force=True ignora o cache em memória e busca da API diretamente.
    Nunca lança exceção — retorna {} em caso de falha total.
    """
    global _memory_cache, _memory_ts
    now = time.time()
    if not force and _memory_cache and now - _memory_ts < _CACHE_TTL:
        return _memory_cache

    api_url = (os.environ.get("DASHBOARD_API_URL") or os.environ.get("AUDITORIA_API_URL", "")).rstrip("/")
    api_token = os.environ.get("DASHBOARD_API_TOKEN") or os.environ.get("AUDITORIA_API_TOKEN", "")
    pdv_station = os.environ.get("PDV_STATION", "001")

    # Normaliza URL: converte http://host:8098 → https://host:8099 automaticamente
    if api_url.startswith("http://") and ":8098" in api_url:
        api_url = api_url.replace("http://", "https://").replace(":8098", ":8099")

    if api_url and api_token:
        try:
            import ssl as _ssl
            import urllib.request as _ur
            ctx = _ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = _ssl.CERT_NONE
            req = _ur.Request(
                f"{api_url}/api/v1/pdv-config?pdv={pdv_station}",
                headers={"Authorization": f"Bearer {api_token}"},
            )
            with _ur.urlopen(req, timeout=5, context=ctx) as resp:
                if resp.status == 200:
                    cfg = json.loads(resp.read())
                    _memory_cache = cfg
                    _memory_ts = now
                    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
                    _CACHE_PATH.write_text(json.dumps(cfg))
                    return cfg
        except Exception:
            pass

    # Fallback: cache em disco (pode estar desatualizado)
    if not _memory_cache:
        try:
            _memory_cache = json.loads(_CACHE_PATH.read_text())
        except Exception:
            _memory_cache = {}

    return _memory_cache
