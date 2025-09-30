# Python 3.7 compatibility utilities
try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

__all__ = ['Annotated']
