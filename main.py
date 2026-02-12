from __future__ import annotations

import argparse
import sys

from maps_scraper import ColetorGoogleMaps
from storage import salvar_leads


def criar_parser() -> argparse.ArgumentParser:

    p = argparse.ArgumentParser(
        prog="prospecbot-mvp",
        description="Coleta leads do Google Maps e exporta CSV/XLSX (MVP público).",
    )
    p.add_argument("--q", "--query", dest="query", required=True, help="Termo de busca. Ex: 'pizzaria Curitiba'")
    p.add_argument("--n", "--limit", dest="limit", type=int, default=30, help="Quantidade de leads (padrão: 30)")
    p.add_argument("--headless", action="store_true", help="Executa Chrome em modo headless")
    p.add_argument("--no-headless", action="store_true", help="Força Chrome visível")
    p.add_argument("--fmt", choices=["csv", "xlsx"], default="csv", help="Formato de export (csv/xlsx)")
    p.add_argument("--delay", type=float, default=0.3, help="Delay (segundos) entre cliques (padrão: 0.3)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = criar_parser().parse_args(argv)

    # Regra simples de precedência:
    # --no-headless ganha do padrão; --headless só reafirma o padrão.
    headless = True
    if args.no_headless:
        headless = False
    elif args.headless:
        headless = True

    coletor = ColetorGoogleMaps(headless=headless)
    coletor.iniciar()
    try:
        leads = coletor.coletar(
            args.query,
            limite=max(1, int(args.limit)),
            delay=max(0.0, float(args.delay)),
        )
    finally:
        coletor.finalizar()

    caminho = salvar_leads(leads, formato=args.fmt)
    print(f"OK: {len(leads)} leads salvos em: {caminho}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))