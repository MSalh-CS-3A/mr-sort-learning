"""Inv-2-MR-Sort. Les imports natifs sont différés jusqu'à l'exécution."""


def main() -> None:
    from .cli import main as cli_main

    raise SystemExit(cli_main())
