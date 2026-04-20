"""
Configuration module for django-compose.

This module provides globally accessible configuration variables that can be
overwritten from outside the library.
"""

from django_compose.base.attributes import Attribute, classes
from typing_extensions import Callable

# Default attribute that can be overridden by external code
attribute_string_handler: Callable[[str], Attribute] = lambda s: classes(s)

__all__ = ["attribute_string_handler"]
