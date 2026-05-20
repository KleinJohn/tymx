from __future__ import annotations

from importlib.util import find_spec

__all__: list[str] = []


def __getattr__(name: str) -> object:
    if name in {"App", "Route", "Router"} and find_spec("django") is None:
        raise ImportError(
            "tymx.django requires the optional 'django' dependency. "
            "Install tymx[django] to use these integrations."
        )
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


if find_spec("django") is not None:
    from ._app import App, Route, Router

    __all__ = ["App", "Route", "Router"]
