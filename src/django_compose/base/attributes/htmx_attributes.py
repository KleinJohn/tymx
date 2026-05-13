from typing import Any, Self

from .base_attributes import (
    BooleanAttribute,
    ComposedAttribute,
    ComposePolicy,
    SimpleAttribute,
)


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
            value = "js:{" + ", ".join(f"{key}: {val}" for key, val in kwargs.items()) + "}"
        else:
            value = "{" + ", ".join(f'"{key}": "{val}"' for key, val in kwargs.items()) + "}"
        return super().__call__(value, init_kwargs=init_kwargs)


# looks like this: js/"":{"key": "value", key2: value2}


comma_composer = ComposePolicy(
    composer=lambda values: ",".join(values),
    decomposer=lambda values: values.split(","),
)
whitespace_composer = ComposePolicy(
    composer=lambda values: " ".join(values),
    decomposer=lambda values: values.split(" "),
)

# see: https://htmx.org/reference/#attributes
hx_get = SimpleAttribute("hx-get")
hx_post = SimpleAttribute("hx-post")
hx_on = SimpleAttribute("hx-on")  # TODO: should be more complex
hx_push_url = SimpleAttribute("hx-push-url")
hx_select = SimpleAttribute("hx-select")
hx_select_oob = ComposedAttribute("hx-select-oob", policy=comma_composer)
hx_swap = SimpleAttribute("hx-swap")
hx_swap_oob = SimpleAttribute("hx-swap-oob")
hx_target = SimpleAttribute("hx-target")
hx_trigger = ComposedAttribute("hx-trigger", policy=comma_composer)
hx_vals = JsonAttribute("hx-vals")

hx_boost = BooleanAttribute("hx-boost", use_true_false=("true", "false"))
hx_confirm = SimpleAttribute("hx-confirm")
hx_delete = SimpleAttribute("hx-delete")
hx_disable = BooleanAttribute("hx-disable")
hx_disabled_elt = SimpleAttribute("hx-disabled-elt")
hx_disinherit = ComposedAttribute("hx-disinherit", policy=whitespace_composer)
hx_encoding = SimpleAttribute("hx-encoding")
hx_ext = ComposedAttribute("hx-ext", policy=comma_composer)
hx_headers = JsonAttribute("hx-headers")
hx_history = BooleanAttribute("hx-history", use_true_false=("true", "false"))
hx_history_elt = BooleanAttribute("hx-history-elt")
hx_include = ComposedAttribute("hx-include", policy=comma_composer)
hx_indicator = SimpleAttribute("hx-indicator")
hx_inherit = ComposedAttribute("hx-inherit", policy=whitespace_composer)
hx_params = ComposedAttribute("hx-params", policy=comma_composer)
hx_patch = SimpleAttribute("hx-patch")
hx_preserve = BooleanAttribute("hx-preserve")
hx_prompt = SimpleAttribute("hx-prompt")
hx_put = SimpleAttribute("hx-put")
hx_replace_url = SimpleAttribute("hx-replace-url")
hx_request = JsonAttribute("hx-request")
hx_sync = SimpleAttribute("hx-sync")
hx_validate = BooleanAttribute("hx-validate", use_true_false=("true", "false"))
