"""Compatibility import; use flux config init and explicit load()."""

from flux.config import Settings, load

__all__ = ["Settings", "load"]
