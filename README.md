# TYMX
A composable, Python components library for building interactive HTML pages - without 
writing a single template.

```py
index_page = Page(head=[bulma.cdn])[
    bulma.Box((bulma.Flex.justify_center))[
        bulma.Button(
            (bulma.Color.DANGER.background, bulma.M.all(2)),
            icon=bulma.Icon("fa fa-rocket"),
            icon_side=bulma.Side.RIGHT,
        )["Launch"],
        bulma.ProgressBar(bulma.Color.DANGER, size=bulma.Size.SMALL),
    ]
]

```

## What is TYMX?
tymx lets you define HTML pages as python object trees.
Components are constructed using bracket notation, styled through 
modifiers and rendered to clean HTML.
You can use the pre-defined css components libraries like bulma CSS or tailwind, 
or create your own components without any boilerplate:

```py
class ProgressBar(Component):

    value: str | None = None
    max_value: str = "100"
    size: Size | None = None

    @override
    def build(self, context: Context) -> Children:
        classes: list[a.Attribute] = [a.classes("progress"), a.max(self.max_value)]
        if self.value is not None:
            classes.append(a.value(self.value))
        if self.size:
            classes.append(a.classes(self.size))

        return html.Progress(classes)[self.children]
```


# Development

## The Process of choosing a dataclass framework

### Why pydantic does not work
There is a lot of friction:
- pydantic adds a lot of validation overhead
- No native support for varargs
- No good way to show a field mapping input type -> output type
- Need to call model_rebuild on every model and have to import every model to work

### Why attrs does not work
- Need to add decorator to every subclass
- No support for varargs
- Better way of handling mapping input type -> output type

### Solution:
Use a modified version of attrs, including a mypy plugin! 
By using a metaclass, the @dataclass_transform decorator and attrs together, 
it is possible to build a version of attrs that works with mypy and enables 
attrs support by subclassing BaseModel (like in pydantic) and also enables us to 
include quality of life additions like auto_frozen.
