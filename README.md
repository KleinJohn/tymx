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


## About Components
Components should not be changed after instantiation outside their own build process.


### The `BaseComponent.build` method
This method should return the components which will replace the calling component 
in the component tree. The `build` method should never return the calling component
or an instance of the same class, 
but instead another component or a copy of itself. The `build` method should not 
return an instance of the calling class by instantiation through the constructor 
or `Component[child]` method, since this will lead to recursion. Instead, use 
`self[child]`, to return a copy which will not call its own `build`, therefore 
breaking recursion. This can be useful if you want to overwrite the component's 
`render` method.

Examples:
```py
# DO call other components with children
def build(context, children):
    return AnotherComponent[children]

# DO nest them arbitrarily
def build(context, children):
    return [
        HeaderComponent[H1["The title"]],
        children,
        AnotherButton(disabled)[
            "press me!"
        ]
    ]

# DO call other components without children
def build(context, children):
    return AnotherComponent

# DO return just the children
def build(context, children):
    return children     # replace this component with its children

# DO return a copy of the component to render it, using __getitem__
def build(context, children):
    return self[children]   # or just self[] to remove children


######## DON'Ts ########

# DON'T return an instance of the component -> instead use self[children]
def build(context, children):   # ThisComponent.build
    return ThisComponent[children]      # or just ThisComponent or something like that

# DON'T return the component itself -> instead use self[] without children
def build(context, children):
    return self
```


### The `BaseComponent.full_build` method
The `full_build` method is supposed to handle the build process of a component
and its children. 


**Why does the Component have to be restored to its original state after `full_build`?**

During the `full_build` method, the Component has to store information about the 
current build state in itself. But we have to consider an instance of a Component 
to be used multiple times in different positions and contexts during one build.
Therefore, to enable sequential `full_build` calls, the method should clean up 
after itself to prevent side effects on subsequent calls. 
We can exclude side effects in nested use contexts of the same instance, e.g.:
```py
component = SomeComponent()
nested_component = component[component]
```
since nesting the original component instance creates a copy of the instance, and 
therefore resets the `build_data` and other state.