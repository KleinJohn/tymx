# from dataclasses import dataclass, field
import builtins
from abc import ABCMeta
from threading import local
from typing import Any, Callable, cast, dataclass_transform
from attrs import define, field, fields
from attrs.exceptions import FrozenInstanceError


_repr_context = local()


# @dataclass_transform(kw_only_default=True, field_specifiers=(field,))
# class ModelBase(metaclass=ModelMeta):

#     def __init_subclass__(cls, **kwargs: Any) -> None:
#         attrs_settings: dict[str, Any] = {"kw_only": True}
#         attrs_settings.update(kwargs)
#         # Automatically apply attrs.define to every new subclass.
#         # attrs modifies the class in place to generate __init__, __eq__, etc.
#         super().__init_subclass__()
#         define(cls, **attrs_settings)


class ModelMeta(type):
    def __new__(
        mcs: type,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> type[Any]:
        frozen = kwargs.pop("frozen", None)
        auto_frozen = kwargs.pop("auto_frozen", None)

        # 1. Prevent recursion from attrs rebuilding the class internally
        if namespace.get("_attrs_is_defining", False):
            return super().__new__(mcs, name, bases, namespace)  # type: ignore

        inherited_auto_frozen = any(
            getattr(b, "__is_auto_frozen__", False) for b in bases
        )
        is_auto_frozen = (
            auto_frozen if auto_frozen is not None else inherited_auto_frozen
        )
        is_frozen = frozen if frozen is not None else is_auto_frozen

        cls: type[Any] = super().__new__(mcs, name, bases, namespace)  # type: ignore

        if name == "ModelBase":
            return cls

        attrs_settings: dict[str, Any] = {"kw_only": True, "repr": False}
        attrs_settings.update(kwargs)

        # 2. Flag the namespace before sending it to attrs
        cls._attrs_is_defining = True

        new_cls = cls
        try:
            new_cls = define(cls, **attrs_settings)
        finally:
            if hasattr(new_cls, "_attrs_is_defining"):
                delattr(new_cls, "_attrs_is_defining")
            if cls is not new_cls and hasattr(cls, "_attrs_is_defining"):
                delattr(cls, "_attrs_is_defining")

        new_cls.__is_frozen__ = is_frozen
        new_cls.__is_auto_frozen__ = is_auto_frozen
        original_setattr = cast(
            Callable[[Any, str, Any], None], getattr(new_cls, "__setattr__")
        )

        def overwrite_frozen_setattr(self: Any, key: str, value: Any) -> None:
            # If the class is flagged as frozen AND initialization is finished, block mutation
            if getattr(self.__class__, "__is_frozen__", False) and getattr(
                self, "__is_init_complete__", False
            ):
                raise FrozenInstanceError(
                    f"Cannot mutate attribute '{key}' on a frozen {self.__class__.__name__} instance."
                )

            # Otherwise, proceed normally (this triggers attrs converters/validators)
            original_setattr(self, key, value)

        setattr(new_cls, "__setattr__", overwrite_frozen_setattr)

        return new_cls


class ModelABCMeta(ModelMeta, ABCMeta):
    pass


@dataclass_transform(kw_only_default=True, field_specifiers=(field,))
class BaseModel(metaclass=ModelABCMeta):
    __is_init_complete__: bool = field(init=False, default=False, repr=False)

    def __attrs_post_init__(self) -> None:
        object.__setattr__(self, "__is_init_complete__", True)

    def __repr__(self) -> str:
        object_id = builtins.id(self)
        already_repring: set[int] = getattr(_repr_context, "already_repring", set())

        if object_id in already_repring:
            return "..."

        _repr_context.already_repring = already_repring
        already_repring.add(object_id)
        try:
            field_reprs: list[str] = []
            for attr_field in fields(self.__class__):
                if attr_field.repr is False:
                    continue
                value = getattr(self, attr_field.name)
                value_repr = (
                    attr_field.repr(value) if callable(attr_field.repr) else repr(value)
                )
                field_reprs.append(f"{attr_field.name}={value_repr}")
            return f"{self.__class__.__qualname__}({', '.join(field_reprs)})"
        finally:
            already_repring.remove(object_id)
