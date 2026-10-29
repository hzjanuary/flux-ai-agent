"""Deprecated entry point; startup now requires the explicit CLI."""

from flux.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
