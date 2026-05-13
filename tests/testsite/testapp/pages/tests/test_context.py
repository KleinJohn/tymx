import unittest

from tymx.base import Page, Router
from tymx.base.app import DjangoApp
from tymx.base.components.html_components import Div
from tymx.base.context import Context, ContextFrame, DataDict
from tymx.base.attributes import Attributes
from tymx.base.modifiers import Modifiers


def make_router_and_page() -> tuple[Router, Page]:
    page = Page(name="index")
    router = Router(DjangoApp(name="testapp", pages=[]), pages=[page])
    return router, page


class ContextTests(unittest.TestCase):

    def test_copy_without_current_frame_keeps_router_page_and_history(self) -> None:
        router, page = make_router_and_page()
        context = Context(router=router, page=page)

        copied = context.copy()

        self.assertIsNot(copied, context)
        self.assertIs(copied.router, context.router)
        self.assertIs(copied.page, context.page)
        self.assertEqual(copied.history, [])
        self.assertIsNot(copied.history, context.history)
        self.assertIsNone(copied._data)

    def test_copy_clones_history_and_current_data(self) -> None:
        router, page = make_router_and_page()
        context = Context(router=router, page=page)

        previous_frame = ContextFrame(
            component=Div(),
            data=DataDict(),
            level=0,
        )
        previous_frame.attributes = Attributes("test-class")
        previous_frame.modifiers = Modifiers()
        context.push_frame(previous_frame)

        context.create_data(Div())
        context.data.attributes = Attributes("test-class")
        context.data.modifiers = Modifiers()

        copied = context.copy()

        self.assertIsNot(copied, context)
        self.assertIsNot(copied.history, context.history)
        self.assertEqual(len(copied.history), 1)
        self.assertIsNot(copied.history[0], previous_frame)
        self.assertIs(copied.history[0].component, previous_frame.component)
        self.assertIsNot(copied.history[0]._data, previous_frame._data)
        self.assertIsNot(copied.data, context.data)
        self.assertIs(copied.data.component, context.data.component)
        self.assertIsNot(copied.data._data, context.data._data)

        copied.history[0].attributes = Attributes()
        self.assertIsNot(copied.history[0].attributes, previous_frame.attributes)
        original_modifiers = context.data.modifiers
        copied.data.modifiers = Modifiers()
        self.assertIs(context.data.modifiers, original_modifiers)
        self.assertIsNot(copied.data.modifiers, context.data.modifiers)


class ContextFrameTests(unittest.TestCase):

    def test_copy_clones_data_dict(self) -> None:
        frame = ContextFrame(
            component=Div(),
            data=DataDict(),
            level=2,
        )
        frame.attributes = Attributes()
        frame.modifiers = Modifiers()

        copied = frame.copy()

        self.assertIsNot(copied, frame)
        self.assertIsNot(copied._data, frame._data)
        self.assertIs(copied.component, frame.component)
        self.assertEqual(copied.level, frame.level)

        copied.attributes = Attributes()
        self.assertIsNot(copied.attributes, frame.attributes)
        copied.modifiers = Modifiers()
        self.assertIsNot(copied.modifiers, frame.modifiers)


if __name__ == "__main__":
    unittest.main()
