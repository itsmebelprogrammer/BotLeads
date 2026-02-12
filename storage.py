from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

COLUNAS_PADRAO = [
    "Nome",
    "Telefone",
    "Site",
    "WhatsApp",
    "Origem",
]


def garantir_pasta_output(diretorio_base: str | Path = ".") -> Path:
    """
    Cria a pasta output/ se não existir.

    """
    out = Path(diretorio_base) / "output"
    out.mkdir(parents=True, exist_ok=True)
    return out


def salvar_leads(leads: list[dict], *, diretorio_base: str | Path = ".", formato: str = "csv") -> Path:
    """
    Salva leads em output/ com timestamp.

    formato:
    - 'csv' (padrão) ou 'xlsx'

    """
    out = garantir_pasta_output(diretorio_base)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    df = pd.DataFrame(leads)

    # Garante as colunas (mesmo que algum lead venha sem telefone/site).
    for c in COLUNAS_PADRAO:
        if c not in df.columns:
            df[c] = ""

    df = df[COLUNAS_PADRAO]

    if formato.lower() in ("xlsx", "excel"):
        caminho = out / f"leads_{ts}.xlsx"
        df.to_excel(caminho, index=False)
        return caminho

    caminho = out / f"leads_{ts}.csv"
    df.to_csv(caminho, index=False, encoding="utf-8-sig")
    return caminho