from tymx.base.components.base_components import Component
from tymx.base.context import Context
from tymx.debug._app import DebugApp, DebugRoute, DebugRouter


def get_context(component: Component) -> Context:
    route = DebugRoute(component=component)
    app = DebugApp(name="TestApp", routes={"debug": route})
    router = DebugRouter(app, routes={"debug": route})
    return Context(router=router)
