"""
Gemini Auditor — serviço de auditoria de cupons via Gemini Vision.
Monitora spy files, detecta cupons fechados e delega análise ao
endpoint /gemini-analyze do video_streamer (que faz captura DVR,
análise Gemini e post na API tudo em um passo).

Configuração (env vars):
  AUDITORIA_API_TOKEN  — token do PDV (obrigatório)
  DVR_DELAY            — segundos aguardar footage após cupom fechar (default: 120)
  PDV_STATION          — identificador do PDV (default: 001)
  STREAMER_URL         — URL base do video_streamer (default: http://127.0.0.1:8765)
"""

import glob as _glob
import json
import logging
import os
import re
import sys
import time
import urllib.request
import urllib.parse
from datetime import date
from pathlib import Path

DVR_DELAY      = int(os.environ.get("DVR_DELAY", "120"))
API_TOKEN      = os.environ.get("AUDITORIA_API_TOKEN", "")
PDV_STATION    = os.environ.get("PDV_STATION", "001")
STREAMER_URL   = os.environ.get("STREAMER_URL", "http://127.0.0.1:8765").rstrip("/")

SPY_DIR        = "/home/rpdv/frente/Cm"
ESTADO_FILE    = "/tmp/gemini_auditor_estado.json"
MARKER_FILE    = "/var/lib/pdv-visual-auditor/measurement_marker.json"
POLL_INTERVAL  = 10

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [gemini_auditor] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.info

# ── Remote config ─────────────────────────────────────────────────────────────
try:
    sys.path.insert(0, "/opt/pdv-visual-auditor")
    import pdv_config_loader as _cfg_loader
    _remote_cfg = _cfg_loader.fetch()
except Exception:
    _cfg_loader = None
    _remote_cfg = {}

_auditoria_enabled = bool(_remote_cfg.get("auditoria_enabled", True))


# ── Estado persistente ────────────────────────────────────────────────────────
def _carregar_estado():
    try:
        return json.load(open(ESTADO_FILE))
    except Exception:
        return {"processados": [], "fila": []}


def _salvar_estado(estado):
    json.dump(estado, open(ESTADO_FILE, "w"))


# ── Stats para o pipeline do dashboard ────────────────────────────────────────
# Formato compatível com o endpoint /vlm-stats do video_streamer (modo cupom).
_stats_hoje: dict = {}   # chave = str(num_cupom)
_stats_data: str  = ""   # data corrente do stats (YYYY-MM-DD)


def _stats_file(data_str: str) -> str:
    return "/tmp/vlm_stats_%s.json" % data_str


def _stats_status(result) -> str:
    if result is None:
        return "INCONCLUSIVO"
    alertas = result.get("alertas", 0)
    itens   = result.get("itens_analisados", 0)
    inc     = result.get("inconclusivos", 0)
    if alertas > 0:
        return "SUSPEITO"
    if itens > 0 and inc == itens:
        return "INCONCLUSIVO"
    return "OK"


def _gravar_stats(fila_size: int):
    hoje = date.today().strftime("%Y-%m-%d")
    rows = _stats_hoje

    ok  = sum(1 for r in rows.values() if r.get("status") == "OK")
    sus = sum(1 for r in rows.values() if r.get("status") == "SUSPEITO")
    inc = sum(1 for r in rows.values() if r.get("status") == "INCONCLUSIVO")
    sem = sum(1 for r in rows.values() if r.get("status") == "SEM_DVR")

    payload = {
        "ok":          ok,
        "suspeito":    sus,
        "inconclusivo": inc,
        "sem_dvr":     sem,
        "fila":        fila_size,
        "cupoms":      rows,
    }
    try:
        Path(_stats_file(hoje)).write_text(json.dumps(payload))
    except Exception as e:
        log("Erro ao gravar stats: %s" % e)

    # Marcador de modo — garante que /vlm-stats use modo cupom
    try:
        Path(MARKER_FILE).parent.mkdir(parents=True, exist_ok=True)
        Path(MARKER_FILE).write_text(json.dumps({"date": hoje, "note": "cupom_mode"}))
    except Exception:
        pass


def _registrar_cupom_fila(num: int):
    _stats_hoje[str(num)] = {"total": 1, "done": 0, "status": "INCOMPLETO"}
    _gravar_stats(sum(1 for r in _stats_hoje.values() if r.get("status") == "INCOMPLETO"))


def _registrar_cupom_resultado(num: int, result):
    status = _stats_status(result)
    total  = result.get("itens_analisados", 1) if result else 1
    _stats_hoje[str(num)] = {
        "total":  total,
        "done":   total,
        "status": status,
        "ok":     result.get("ok", 0) if result else 0,
        "sus":    result.get("alertas", 0) if result else 0,
        "inc":    result.get("inconclusivos", 0) if result else 0,
    }
    fila_size = sum(1 for r in _stats_hoje.values() if r.get("status") == "INCOMPLETO")
    _gravar_stats(fila_size)


# ── Spy file ──────────────────────────────────────────────────────────────────
def _spy_file_hoje():
    hoje = date.today().strftime("%d%m%y")
    files = _glob.glob(os.path.join(SPY_DIR, "Espiao%s.001" % hoje))
    if files:
        return files[0]
    all_files = sorted(_glob.glob(os.path.join(SPY_DIR, "Espiao*.001")), reverse=True)
    return all_files[0] if all_files else None


_FECHACUPOM_RE = re.compile(r"^(\d{2}:\d{2}:\d{2}):FECHACUPOM\s*\|\s*Cod:\s*(\d+)\s*\|")


def _ler_cupons_fechados(spy_file):
    cupons = []
    data_hoje = date.today().strftime("%Y-%m-%d")
    try:
        for line in open(spy_file, errors="replace"):
            m = _FECHACUPOM_RE.match(line)
            if m:
                cupons.append((int(m.group(2)), m.group(1), data_hoje))
    except Exception:
        pass
    return cupons


# ── Chamar o endpoint Gemini no streamer ──────────────────────────────────────
def _chamar_gemini_analyze(cupom_num):
    url = "%s/gemini-analyze?cupom=%s&token=%s" % (
        STREAMER_URL,
        urllib.parse.quote(str(cupom_num)),
        urllib.parse.quote(API_TOKEN),
    )
    try:
        req = urllib.request.Request(url, method="POST")
        req.add_header("Content-Length", "0")
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read())
    except Exception as e:
        log("Erro ao chamar /gemini-analyze cupom %s: %s" % (cupom_num, e))
        return None


# ── Loop principal ────────────────────────────────────────────────────────────
def main():
    global _auditoria_enabled

    if not API_TOKEN:
        print("ERRO: AUDITORIA_API_TOKEN nao definida")
        sys.exit(1)

    log("Gemini Auditor iniciado | DVR_DELAY=%ds | PDV=%s" % (DVR_DELAY, PDV_STATION))

    estado = _carregar_estado()
    processados = set(estado.get("processados", []))
    fila = estado.get("fila", [])
    _last_cfg_refresh = 0.0

    while True:
        agora = time.time()

        # Refresh remoto a cada 5 min
        if agora - _last_cfg_refresh >= 300 and _cfg_loader:
            try:
                rcfg = _cfg_loader.fetch(force=True)
                _auditoria_enabled = bool(rcfg.get("auditoria_enabled", True))
            except Exception:
                pass
            _last_cfg_refresh = agora

        if not _auditoria_enabled:
            time.sleep(POLL_INTERVAL)
            continue

        # 1. Processar cupons cujo delay já passou
        prontos = [f for f in fila if agora >= f[3]]
        fila    = [f for f in fila if agora < f[3]]

        for num, hora, data_cupom, _ in prontos:
            log("Processando cupom %d (DVR_DELAY expirado)" % num)
            result = _chamar_gemini_analyze(num)
            if result:
                log("Cupom %d: %d itens | ok=%d alertas=%d inc=%d | R$%.4f" % (
                    num,
                    result.get("itens_analisados", 0),
                    result.get("ok", 0),
                    result.get("alertas", 0),
                    result.get("inconclusivos", 0),
                    result.get("custo_brl", 0.0),
                ))
            _registrar_cupom_resultado(num, result)
            processados.add(num)
            if len(processados) > 500:
                processados = set(sorted(processados)[-500:])

        # 2. Varrer spy file por novos cupons fechados
        spy = _spy_file_hoje()
        if spy:
            fechados = _ler_cupons_fechados(spy)
            na_fila  = {f[0] for f in fila}
            novos    = 0
            for num, hora, data_cupom in fechados:
                if num not in processados and num not in na_fila:
                    ts_analise = agora + DVR_DELAY
                    fila.append([num, hora, data_cupom, ts_analise])
                    _registrar_cupom_fila(num)
                    novos += 1
                    log("Cupom %d fechado às %s — agendado em %ds" % (num, hora, DVR_DELAY))
            if novos > 0 or prontos:
                _salvar_estado({"processados": list(processados), "fila": fila})

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
