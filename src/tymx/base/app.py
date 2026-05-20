from __future__ import annotations

from abc import abstractmethod, ABC
from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Any, Generic, TypeVar, get_args

from tymx.base.components import Component, Page
from tymx.base.context import Context
from tymx.base.helpers.base_model import BaseModel

if TYPE_CHECKING:
    from tymx.base.app import AbstractApp


_T_Route = TypeVar("_T_Route", bound="AbstractRoute")
_T_Router = TypeVar("_T_Router", bound="AbstractRouter")


class AbstractRoute(BaseModel):
    app_name: str
    page: Page

    @property
    @abstractmethod
    def url(self) -> str:
        """Only call this when Django is fully loaded (render time)"""
        ...


class AbstractRouter(Generic[_T_Route], ABC):
    __factory__: type[_T_Route]

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)

        # Look at the base classes of the new subclass
        # __orig_bases__ contains the Generic[Type] info
        for base in getattr(cls, "__orig_bases__", []):
            args = get_args(base)
            if args:
                cls.__factory__ = args[0]
                break

    def __init__(self, app: AbstractApp, *, pages: Iterable[Page], **view_kwargs: Any):
        self.app = app
        self.routes: dict[str, _T_Route] = {
            page.name: self.__factory__(app_name=self.app.name, page=page)
            for page in pages
        }
        self._view_kwargs = view_kwargs
        self._iter = iter(self.routes.values())

    def __iter__(self) -> Iterator[AbstractRoute]:
        self._iter = iter(self.routes.values())
        return self._iter

    def __next__(self) -> AbstractRoute:
        return next(self._iter)

    def get_url(self, page_name: str) -> str:
        route = self.routes.get(page_name)
        if route is None:
            raise ValueError(f"Route '{page_name}' not found in router.")
        return route.url

    @abstractmethod
    def get_urlpatterns(self) -> Any: ...


class AbstractApp(Generic[_T_Router], ABC):
    __factory__: type[_T_Router]

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)

        # Look at the base classes of the new subclass
        # __orig_bases__ contains the Generic[Type] info
        for base in getattr(cls, "__orig_bases__", []):
            args = get_args(base)
            if args:
                cls.__factory__ = args[0]
                break

    def __init__(
        self,
        *,
        name: str,
        pages: Iterable[Page],
    ):
        self.name = name
        self.router = type(self).__factory__(app=self, pages=pages)
        # App-level cache for built (document-level) page results. Keyed by page name.
        self.built_pages: dict[str, Component] = {}

    def build(self) -> None:
        context = Context(router=self.router)
        for route in self.router:
            built = route.page.full_build(context)
            # can access [0] since page returns single html component
            self.built_pages[route.page.name] = built[0]
