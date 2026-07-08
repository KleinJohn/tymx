import unittest

from tymx.base.attributes import Attribute, classes, id, style
from tymx.base.components.html_components import Div
from tymx.base.modifiers import Modifier


class FirstModifier(Modifier):
    label: str


class SecondModifier(Modifier):
    label: str


class TestMatmulComposition(unittest.TestCase):
    def test_attribute_matmul_merges_left_to_right(self):
        merged = id("one") @ classes("btn") @ id("two") @ style("color:red")

        self.assertIsInstance(merged, tuple)
        self.assertEqual(len(merged), 3)
        self.assertTrue(all(isinstance(attr, Attribute) for attr in merged))
        self.assertEqual([attr.name for attr in merged], ["id", "class", "style"])  # type: ignore
        self.assertEqual([attr.value for attr in merged], ["two", "btn", "color:red;"])  # type: ignore

    def test_attributes_can_wrap_around_a_component(self):
        left_attributes = id("one") @ classes("btn")
        right_attributes = id("two") @ style("background:blue")
        component = left_attributes @ Div()["body"] @ right_attributes

        self.assertEqual(component.attributes["id"].value, "two")
        self.assertEqual(str(component.attributes["class"]), 'class="btn"')
        self.assertEqual(str(component.attributes["style"]), 'style="background:blue;"')

    def test_modifier_matmul_merges_left_to_right(self):
        merged = FirstModifier(label="one") @ SecondModifier(label="two")

        self.assertIsInstance(merged, tuple)
        self.assertEqual(len(merged), 2)
        self.assertTrue(all(isinstance(mod, Modifier) for mod in merged))
        self.assertEqual([type(mod) for mod in merged], [FirstModifier, SecondModifier])
        self.assertEqual([mod.label for mod in merged], ["one", "two"])  # type: ignore

    def test_modifiers_can_wrap_around_a_component(self):
        left_modifiers = FirstModifier(label="one") @ SecondModifier(label="two")
        component = left_modifiers @ Div()["body"]

        self.assertEqual(
            [type(mod) for mod in component.modifiers],
            [FirstModifier, SecondModifier],
        )
        self.assertEqual([mod.label for mod in component.modifiers], ["one", "two"])  # type: ignore
        self.assertEqual(component.children[0].text, "body")  # type: ignore

    def test_interleaved_attributes_and_modifiers_wrap_component(self):
        component = (
            id("one")
            @ FirstModifier(label="first")
            @ classes("btn")
            @ SecondModifier(label="second")
            @ Div()["body"]
        )

        self.assertEqual(component.attributes["id"].value, "one")
        self.assertEqual(str(component.attributes["class"]), 'class="btn"')
        self.assertEqual(
            [type(mod) for mod in component.modifiers],
            [FirstModifier, SecondModifier],
        )
        self.assertEqual(
            [mod.label for mod in component.modifiers], ["first", "second"]  # type: ignore
        )
        self.assertEqual(component.children[0].text, "body")  # type: ignore


if __name__ == "__main__":
    unittest.main()
