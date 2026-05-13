import unittest

from tymx.base.attributes import Attributes
from tymx.base.attributes import classes, id, style


class TestAttributesMerging(unittest.TestCase):

    def test_merge_attributes_overwrites_by_default(self):
        a1 = Attributes([id("one"), classes("btn")])
        a2 = Attributes([id("two"), classes("primary")])

        merged = a1 | a2

        self.assertEqual(merged["id"].value, "two")
        # composed classes should preserve order and include both values
        self.assertIn("btn", merged["class"])
        self.assertIn("primary", merged["class"])
        self.assertEqual(str(merged["class"]), 'class="btn primary"')

    def test_add_overwrite_false_keeps_existing(self):
        attrs = Attributes([id("one")])
        # adding with overwrite=False should keep the original value
        attrs.add(id("two"), overwrite=False)
        self.assertEqual(attrs["id"].value, "one")

    def test_update_overwrite_false_keeps_existing(self):
        attrs = Attributes([id("one")])
        other = Attributes([id("two")])
        attrs.update(other, overwrite=False)
        self.assertEqual(attrs["id"].value, "one")

    def test_composed_attribute_merge_removes_duplicates_and_preserves_order(self):
        a1 = Attributes([classes("a", "b")])
        a2 = Attributes([classes("b", "c")])

        merged = a1 | a2

        # result should be 'a b c'
        self.assertEqual(str(merged["class"]), 'class="a b c"')

    def test_style_composed_with_kwargs_and_merge(self):
        s1 = Attributes([style("color:red")])
        s2 = Attributes([style({"background": "blue"})])

        merged = s1 | s2

        # style composer appends a trailing semicolon
        self.assertEqual(str(merged["style"]), 'style="color:red;background:blue;"')


if __name__ == "__main__":
    unittest.main()
