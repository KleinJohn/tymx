from tymx.base.components import Stylesheet
import tymx.base.attributes as a


cdn = Stylesheet(href="https://cdn.jsdelivr.net/npm/bulma@1.0.4/css/bulma.min.css")


fontawesome_cdn = Stylesheet(
    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"
)


clearfix = a.class_("is-clearfix")
"""Fixes an element's floating children"""

pulled_left = a.class_("is-pulled-left")
"""Moves an element to the left"""

pulled_right = a.class_("is-pulled-right")
"""Moves an element to the right"""

overlay = a.class_("is-overlay")
"""Completely covers the first positioned parent"""

clipped = a.class_("is-clipped")
"""Adds overflow hidden"""

radiusless = a.class_("is-radiusless")
"""Removes any radius"""

shadowless = a.class_("is-shadowless")
"""Removes any shadow"""

unselectable = a.class_("is-unselectable")
"""Prevents the text from being selectable"""

clickable = a.class_("is-clickable")
"""Applies cursor: pointer !important to the element."""

relative = a.class_("is-relative")
"""Applies position: relative to the element."""

