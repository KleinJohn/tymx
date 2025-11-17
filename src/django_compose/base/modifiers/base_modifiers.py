from abc import ABC, abstractmethod
from typing import Self


class Modifier(ABC):

    @abstractmethod
    def __call__(self) -> Self:
        pass


class Attributes(Modifier):

    def __call__(self) -> Self:
        pass

    def __str__(self) -> str:
        return ", ".join(
            f'{attribute}="{value}"' for attribute, value in self._values.items()
        )

    def __or__(self, other: "Attributes") -> "Attributes":
        dict_union = self.values | other.values
        return Attribute(*dict_union.keys(), values=dict_union.values())

    def __ror__(self, other: "Attributes") -> "Attributes":
        return self.__or__(other)

    def __ior__(self, other: "Attributes") -> None:
        self._values.update(other.values)

    @property
    def attributes(self) -> Iterable[str]:
        return self._values.keys()

    @property
    def values(self) -> OrderedDict[str, Any]:
        return self._values
