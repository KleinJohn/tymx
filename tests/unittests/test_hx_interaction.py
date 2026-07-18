import unittest

from tymx.hx._helpers import EventModifier, HxSwap, HxTrigger, PointerEvent


class TestHxSwap(unittest.TestCase):
    def test_hx_swap_all_modifiers(self):
        swap = HxSwap(
            "#my-target",
            transition=True,
            ignore_title=False,
            focus_scroll=True,
            swap="outerHTML",
            settle="load",
            scroll="top",
            show_element="#my-element",
            show="top",
        )
        expected_str = (
            "#my-target transition:true ignore_title:false focus_scroll:true "
            "swap:outerHTML settle:load scroll:top show:#my-element:top"
        )
        self.assertEqual(str(swap), expected_str)

    def test_hx_swap_only_target(self):
        swap = HxSwap("#my-target")
        expected_str = "#my-target"
        self.assertEqual(str(swap), expected_str)

    def test_hx_swap_only_modifiers(self):
        swap = HxSwap(
            None,
            transition=True,
            ignore_title=False,
            focus_scroll=True,
            swap="outerHTML",
            settle="load",
            scroll="top",
            show_element="#my-element",
            show="top",
        )
        expected_str = (
            "transition:true ignore_title:false focus_scroll:true "
            "swap:outerHTML settle:load scroll:top show:#my-element:top"
        )
        self.assertEqual(str(swap), expected_str)

    def test_hx_swap_empty(self):
        swap = HxSwap()
        expected_str = ""
        self.assertEqual(str(swap), expected_str)


class TestHxTrigger(unittest.TestCase):
    def test_hx_trigger_only_event(self):
        trigger = HxTrigger("click")
        expected_str = "click"
        self.assertEqual(str(trigger), expected_str)
        trigger = HxTrigger(PointerEvent.POINTERDOWN)
        expected_str = "pointerdown"
        self.assertEqual(str(trigger), expected_str)

    def test_hx_trigger_every(self):
        trigger = HxTrigger(every="5s")
        expected_str = "every 5s"
        self.assertEqual(str(trigger), expected_str)

    def test_hx_trigger_empty(self):
        self.assertRaises(ValueError, lambda: HxTrigger())

    def test_hx_trigger_event_and_every(self):
        self.assertRaises(ValueError, lambda: HxTrigger("click", every="5s"))

    def test_hx_trigger_with_modifiers(self):
        trigger = HxTrigger("click", modifiers=["once", "delay:500ms"])
        expected_str = "click once delay:500ms"
        self.assertEqual(str(trigger), expected_str)
        trigger = HxTrigger(
            PointerEvent.POINTERDOWN,
            modifiers=[EventModifier("once"), EventModifier(delay="500ms")],
        )
        expected_str = "pointerdown once delay:500ms"
        self.assertEqual(str(trigger), expected_str)

    def test_hx_trigger_with_filter(self):
        trigger = HxTrigger("input", filter="type='text'")
        expected_str = "input[type='text']"
        self.assertEqual(str(trigger), expected_str)

    def test_hx_trigger_with_event_modifiers_and_filter(self):
        trigger = HxTrigger("input", modifiers=["once"], filter="type='text'")
        expected_str = "input[type='text'] once"
        self.assertEqual(str(trigger), expected_str)


if __name__ == "__main__":
    unittest.main()
