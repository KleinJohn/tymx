from .base_attributes import *


class JsonAttribute(SimpleAttribute):

    def __call__(
        self,
        value: str | None = None,
        js: bool = False,
        *,
        init_kwargs: dict[str, Any] | None = None,
        **kwargs: str,
    ) -> Self:
        if js:
            value = (
                "js:{" + ", ".join(f"{key}: {val}" for key, val in kwargs.items()) + "}"
            )
        else:
            value = (
                "{"
                + ", ".join(f'"{key}": "{val}"' for key, val in kwargs.items())
                + "}"
            )
        return super().__call__(value, init_kwargs=init_kwargs)


# looks like this: js/javascript/"":{"key": "value", key2: value2}


commaComposer = ComposePolicy(lambda values: ",".join(values))

# see: https://htmx.org/reference/#attributes
hx_get = SimpleAttribute("hx-get")
hx_post = SimpleAttribute("hx-post")
hx_on = SimpleAttribute("hx-on")  # TODO: should be more complex
hx_push_url = SimpleAttribute("hx-push-url")
hx_select = SimpleAttribute("hx-select")
hx_select_oob = ComposedAttribute("hx-select-oob", compose_policy=commaComposer)
hx_swap = SimpleAttribute("hx-swap")
hx_swap_oob = SimpleAttribute("hx-swap-oob")
hx_target = SimpleAttribute("hx-target")
hx_trigger = ComposedAttribute("hx-trigger", compose_policy=commaComposer)
hx_vals = JsonAttribute("hx-vals")

hx_boost = BooleanAttribute("hx-boost", use_true_false=("true", "false"))
hx_confirm = SimpleAttribute("hx-confirm")
hx_delete = SimpleAttribute("hx-delete")
