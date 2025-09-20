from importlib.metadata import version

from fngen.resources import Fleet
from fngen.decorators import webapp

__version__ = version("fngen")

__all__ = [
    "Fleet",
    "webapp",
    "__version__",
]
