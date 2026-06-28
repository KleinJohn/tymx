from __future__ import annotations

from typing import override

from tymx.base.app import AbstractApp, AbstractRoute, AbstractRouter
from tymx.base.components import Component


def _normalize_path(path: str) -> str:
	if not path:
		return "/"
	return path if path.startswith("/") else f"/{path}"


class DebugRoute(AbstractRoute, frozen=True):
    route_pattern: str | None = None


class DebugRouter(AbstractRouter[DebugRoute]):

	@override
	def get_urlpatterns(self) -> list[tuple[str, Component]]:
		urlpatterns: list[tuple[str, Component]] = []
		for name, route in self.routes.items():
			component = self.app.built_pages.get(name, route.component)
			route_pattern = f"{name}/" if route.route_pattern is None else route.route_pattern
			urlpatterns.append((_normalize_path(route_pattern), component))
		return urlpatterns

	@override
	def get_url(self, route: DebugRoute) -> str:
		name = next((key for key, value in self.routes.items() if value is route), None)
		if name is None:
			raise ValueError("Route not found in router.")

		route_pattern = f"{name}/" if route.route_pattern is None else route.route_pattern
		return _normalize_path(route_pattern)


class DebugApp(AbstractApp[DebugRouter]):
	pass
