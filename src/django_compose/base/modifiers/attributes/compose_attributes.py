class SideModifier:

    def __call__(
        self,
        p: int | None = None,
        x: int | None = None,
        y: int | None = None,
        t: int | None = None,
        b: int | None = None,
        l: int | None = None,
        r: int | None = None,
    ):
        self.p = p
        self.x = x
        self.y = y
        self.t = p
        self.b = p
        self.l = p
        self.r = p
        self.t = x if x is not None else self.t
        self.b = x if x is not None else self.b
        self.l = y if y is not None else self.l
        self.r = y if y is not None else self.r
        self.t = t if t is not None else self.t or 0
        self.b = b if b is not None else self.b or 0
        self.l = l if l is not None else self.l or 0
        self.r = r if r is not None else self.r or 0


class P(SideModifier):

    @property
    def css(self) -> str | None:
        return f"padding: {self.t}px {self.r}px {self.b}px {self.l}px;"


class M(SideModifier):

    @property
    def css(self) -> str | None:
        return f"margin: {self.t}px {self.r}px {self.b}px {self.l}px;"
