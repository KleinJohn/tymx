import unittest
from django_compose.base.components import *


class TestComponentBase(unittest.TestCase):
    def test_policies(self):
        self.assertEqual(ComponentBase.inheritance_policy, BuildPolicy.COMPONENTS)
        self.assertEqual(ComponentBase.build_policy, BuildPolicy.COMPONENTS)


class TestDocumentLevelComponent(unittest.TestCase):
    def test_policies(self):
        self.assertEqual(
            DocumentLevelComponent.inheritance_policy, BuildPolicy.CHILDREN
        )
        self.assertEqual(DocumentLevelComponent.build_policy, BuildPolicy.CHILDREN)


class TestHtmlComponent(unittest.TestCase):
    def test_policies(self):
        self.assertEqual(HtmlComponent.inheritance_policy, BuildPolicy.CHILDREN)
        self.assertEqual(HtmlComponent.build_policy, BuildPolicy.CHILDREN)


if __name__ == "__main__":
    unittest.main()
