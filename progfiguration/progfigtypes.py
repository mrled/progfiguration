"""Progfiguration types

Things here should not depend on any other parts of the progfiguration package
"""


from importlib.abc import Traversable
from pathlib import Path as PathlibPath
from typing import Union
from zipfile import Path as ZipfilePath


AnyPath = Union[PathlibPath, Traversable, ZipfilePath]
"""A pathlib.Path, a Traversable, or a zipfile.Path"""

AnyPathOrStr = Union[AnyPath, str]
"""A pathlib.Path, a Traversable, a zipfile.Path, or a str"""

PathOrStr = Union[PathlibPath, str]
"""A pathlib.Path or a str only

Traversable and zipfile.Path cannot be copied to and do not have .exists(),
so it's useful to have a type that excludes them.
"""


class Bunch:
    """A nice little object wrapper.

    From <https://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/?in=user-97991>
    """

    def __init__(self, **kwds):
        self.__dict__.update(kwds)
