import unittest
from django_compose.base.components import *


class TestComponentBase(unittest.TestCase):
    def test_policies(self):
        self.assertEqual(ComponentBase.inheritance_policy, ComponentPolicy.COMPONENTS)
        self.assertEqual(ComponentBase.build_policy, ComponentPolicy.COMPONENTS)


class TestDocumentLevelComponent(unittest.TestCase):
    def test_policies(self):
        self.assertEqual(
            DocumentLevelComponent.inheritance_policy, ComponentPolicy.CHILDREN
        )
        self.assertEqual(DocumentLevelComponent.build_policy, ComponentPolicy.CHILDREN)


class TestHtmlComponent(unittest.TestCase):
    def test_policies(self):
        self.assertEqual(HtmlComponent.inheritance_policy, ComponentPolicy.CHILDREN)
        self.assertEqual(HtmlComponent.build_policy, ComponentPolicy.CHILDREN)


if __name__ == "__main__":
    unittest.main()
