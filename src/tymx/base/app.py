from __future__ import annotations

from abc import abstractmethod, ABC
from typing import TYPE_CHECKING, Any, Generic, TypeVar, get_args

from attrs import field

from tymx.base.components import Component, Page
from tymx.base.context import Context
from tymx.base.helpers.base_model import BaseModel

if TYPE_CHECKING:
    from tymx.base.app import AbstractApp


_T_Route = TypeVar("_T_Route", bound="AbstractRoute")
_T_Router = TypeVar("_T_Router", bound="AbstractRouter")


class AbstractRoute(BaseModel, frozen=True):
    component: Component = field(kw_only=False)


class AbstractRouter(Generic[_T_Route], ABC):
    __route_factory__: type[_T_Route]

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)

        # Look at the base classes of the new subclass
        # __orig_bases__ contains the Generic[Type] info
        for base in getattr(cls, "__orig_bases__", []):
            args = get_args(base)
            if args:
                cls.__route_factory__ = args[0]
                break

    def __init__(self, app: AbstractApp, *, routes: dict[str, _T_Route]):
        self.app = app
        self.routes = routes

    def get_page_url(self, page_name: str) -> str:
        route = self.routes.get(page_name)
        if route is None:
            raise ValueError(f"Route '{page_name}' not found in router.")
        return self.get_url(route)

    @abstractmethod
    def get_url(self, route: _T_Route) -> str: ...

    @abstractmethod
    def get_urlpatterns(self) -> Any: ...


class AbstractApp(Generic[_T_Router], ABC):
    __router_factory__: type[_T_Router]

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)

        # Look at the base classes of the new subclass
        # __orig_bases__ contains the Generic[Type] info
        for base in getattr(cls, "__orig_bases__", []):
            args = get_args(base)
            if args:
                cls.__router_factory__ = args[0]
                break

    def __init__(
        self,
        *,
        name: str,
        pages: dict[str, Page] | None = None,
        routes: dict[str, _T_Route] | None = None,
    ):
        if pages is None and routes is None:
            raise ValueError("At least one of 'pages' or 'routes' must be provided.")
        merged_routes = {
            n: self.__router_factory__.__route_factory__(component=page)
            for n, page in (pages or {}).items()
        } | (routes or {})
        self.name = name
        self.router = self.__router_factory__(app=self, routes=merged_routes)
        # App-level cache for built (document-level) page results. Keyed by page name.
        self.built_pages: dict[str, Component] = {}

    def build(self) -> None:
        for name, route in self.router.routes.items():
            context = Context(router=self.router, route=route)
            built = route.component.full_build(context)
            # can access [0] since page returns single html component
            self.built_pages[name] = built[0]
