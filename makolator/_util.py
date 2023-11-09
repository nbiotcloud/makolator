#
# MIT License
#
# Copyright (c) 2023 nbiotcloud
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""
Utilties.
"""
import logging
from pathlib import Path
from typing import Iterable, List, Union

Paths = Union[Path, Iterable[Path]]
LOGGER = logging.getLogger("makolator")


def norm_paths(paths: Paths) -> List[Path]:
    """Normalize Single Path or List of Paths to List of Paths."""
    try:
        return list(paths)  # type: ignore
    except TypeError:
        return [paths]  # type: ignore


def check_indent(filepath: Path, lineno: int, beginindent, endindent):
    """Check ``BEGIN``/``END`` indent."""
    if endindent != beginindent:
        LOGGER.warning(
            "'%s:%d' Indent of END tag %r does not match indent of BEGIN tag %r.",
            filepath,
            lineno,
            endindent,
            beginindent,
        )


def humanify(iterable):
    """Just join names from `iterable`."""
    if iterable:
        return ", ".join(repr(str(item)) for item in iterable)
    return "''"
