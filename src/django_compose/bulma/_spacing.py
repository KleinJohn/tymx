from __future__ import annotations
from typing import ClassVar, Literal, Self, final, override

from attrs import define, field

type _valid_values = Literal[None, "0", "1", "2", "3", "4", "5", "6", "auto"]


@define(kw_only=True, slots=True, frozen=True)
class _Spacing(str):
    """Represents a spacing value that can be used in Bulma classes."""

    valid_values: ClassVar[set[_valid_values]] = {
        None,
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "auto",
    }

    _basename: str = field(alias="basename", kw_only=False)
    _t: _valid_values = field(alias="t", default=None)
    _r: _valid_values = field(alias="r", default=None)
    _b: _valid_values = field(alias="b", default=None)
    _l: _valid_values = field(alias="l", default=None)

    @override
    def __new__(
        cls,
        basename: str,
        *,
        t: _valid_values = None,
        r: _valid_values = None,
        b: _valid_values = None,
        l: _valid_values = None,
        **kwargs,
    ):
        obj = super().__new__(
            cls, cls.from_values(basename=basename, t=t, r=r, b=b, l=l), **kwargs
        )
        object.__setattr__(obj, "_t", t)
        object.__setattr__(obj, "_r", r)
        object.__setattr__(obj, "_b", b)
        object.__setattr__(obj, "_l", l)
        return obj

    @classmethod
    def validate_values(
        cls,
        *,
        t: str | None = None,
        r: str | None = None,
        b: str | None = None,
        l: str | None = None,
    ) -> None:
        for value in (t, r, b, l):
            if value not in cls.valid_values:
                raise ValueError(
                    f"Invalid spacing value: {value}. Valid values are: {cls.valid_values}"
                )

    @classmethod
    def from_values(
        cls,
        basename: str,
        *,
        t: str | None = None,
        r: str | None = None,
        b: str | None = None,
        l: str | None = None,
    ) -> str:
        cls.validate_values(t=t, r=r, b=b, l=l)
        if t is None and r is None and b is None and l is None:
            return ""
        parts = []
        if t == r == b == l:
            parts.append(f"{basename}-{t}")
        elif t == b and t is not None:
            parts.append(f"{basename}y-{t}")
        elif r == l and r is not None:
            parts.append(f"{basename}x-{r}")
        else:
            if t is not None:
                parts.append(f"{basename}t-{t}")
            if r is not None:
                parts.append(f"{basename}r-{r}")
            if b is not None:
                parts.append(f"{basename}b-{b}")
            if l is not None:
                parts.append(f"{basename}l-{l}")
        return " ".join(parts)

    @override
    def __str__(self) -> str:
        return self

    def with_values(
        self,
        *,
        t: str | None = None,
        r: str | None = None,
        b: str | None = None,
        l: str | None = None,
    ) -> Self:
        return self.__class__(
            basename=self._basename,
            t=t or self._t,
            r=r or self._r,
            b=b or self._b,
            l=l or self._l,
        )

    @property
    def r0(self) -> Self:
        return self.with_values(r="0")

    @property
    def r1(self) -> Self:
        return self.with_values(r="1")

    @property
    def r2(self) -> Self:
        return self.with_values(r="2")

    @property
    def r3(self) -> Self:
        return self.with_values(r="3")

    @property
    def r4(self) -> Self:
        return self.with_values(r="4")

    @property
    def r5(self) -> Self:
        return self.with_values(r="5")

    @property
    def r6(self) -> Self:
        return self.with_values(r="6")

    @property
    def r_auto(self) -> Self:
        return self.with_values(r="auto")

    @property
    def t0(self) -> Self:
        return self.with_values(t="0")

    @property
    def t1(self) -> Self:
        return self.with_values(t="1")

    @property
    def t2(self) -> Self:
        return self.with_values(t="2")

    @property
    def t3(self) -> Self:
        return self.with_values(t="3")

    @property
    def t4(self) -> Self:
        return self.with_values(t="4")

    @property
    def t5(self) -> Self:
        return self.with_values(t="5")

    @property
    def t6(self) -> Self:
        return self.with_values(t="6")

    @property
    def t_auto(self) -> Self:
        return self.with_values(t="auto")

    @property
    def b0(self) -> Self:
        return self.with_values(b="0")

    @property
    def b1(self) -> Self:
        return self.with_values(b="1")

    @property
    def b2(self) -> Self:
        return self.with_values(b="2")

    @property
    def b3(self) -> Self:
        return self.with_values(b="3")

    @property
    def b4(self) -> Self:
        return self.with_values(b="4")

    @property
    def b5(self) -> Self:
        return self.with_values(b="5")

    @property
    def b6(self) -> Self:
        return self.with_values(b="6")

    @property
    def b_auto(self) -> Self:
        return self.with_values(b="auto")

    @property
    def l0(self) -> Self:
        return self.with_values(l="0")

    @property
    def l1(self) -> Self:
        return self.with_values(l="1")

    @property
    def l2(self) -> Self:
        return self.with_values(l="2")

    @property
    def l3(self) -> Self:
        return self.with_values(l="3")

    @property
    def l4(self) -> Self:
        return self.with_values(l="4")

    @property
    def l5(self) -> Self:
        return self.with_values(l="5")

    @property
    def l6(self) -> Self:
        return self.with_values(l="6")

    @property
    def l_auto(self) -> Self:
        return self.with_values(l="auto")

    @property
    def x0(self) -> Self:
        return self.with_values(r="0", l="0")

    @property
    def x1(self) -> Self:
        return self.with_values(r="1", l="1")

    @property
    def x2(self) -> Self:
        return self.with_values(r="2", l="2")

    @property
    def x3(self) -> Self:
        return self.with_values(r="3", l="3")

    @property
    def x4(self) -> Self:
        return self.with_values(r="4", l="4")

    @property
    def x5(self) -> Self:
        return self.with_values(r="5", l="5")

    @property
    def x6(self) -> Self:
        return self.with_values(r="6", l="6")

    @property
    def x_auto(self) -> Self:
        return self.with_values(r="auto", l="auto")

    @property
    def y0(self) -> Self:
        return self.with_values(t="0", b="0")

    @property
    def y1(self) -> Self:
        return self.with_values(t="1", b="1")

    @property
    def y2(self) -> Self:
        return self.with_values(t="2", b="2")

    @property
    def y3(self) -> Self:
        return self.with_values(t="3", b="3")

    @property
    def y4(self) -> Self:
        return self.with_values(t="4", b="4")

    @property
    def y5(self) -> Self:
        return self.with_values(t="5", b="5")

    @property
    def y6(self) -> Self:
        return self.with_values(t="6", b="6")

    @property
    def y_auto(self) -> Self:
        return self.with_values(t="auto", b="auto")


P = _Spacing("p")
M = _Spacing("m")
