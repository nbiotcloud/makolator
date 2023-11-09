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
"""Static Code Preservation."""
import re
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterator, List, Optional

from attrs import define, field

from ._util import LOGGER, check_indent, humanify
from .exceptions import MakolatorError

StaticCodeMap = Dict[str, str]

# pylint: disable=too-few-public-methods


@define
class Info:

    """Static Code Context Information."""

    lineno: int
    indent: str
    name: str


@define
class StaticCode:

    """Static Code Manager."""

    comment_sep: str
    marker: str
    staticcodemap: StaticCodeMap

    _names: List[str] = field(factory=list)

    def __call__(self, name, default=None, comment_sep=None):
        if name in self._names:
            raise MakolatorError(f"duplicate static code {name!r}")
        self._names.append(name)
        if comment_sep is None:
            comment_sep = self.comment_sep or ""
        code = self.staticcodemap.pop(name, default) or ""
        cpre = f"{comment_sep} " if comment_sep else ""
        lines = [f"{cpre}{self.marker} BEGIN {name}"]
        lines.extend(code.splitlines())
        lines.append(f"{cpre}{self.marker} END {name}")
        return "\n".join(lines)


@contextmanager
def read(filepath: Optional[Path], comment_sep: str, marker: str) -> Iterator[StaticCode]:
    """Read from ``filepath``."""
    staticcodemap: StaticCodeMap = {}
    _read(filepath, marker, staticcodemap)
    yield StaticCode(comment_sep, marker, staticcodemap)
    if staticcodemap:
        names = humanify(staticcodemap)
        raise MakolatorError(f"'{filepath!s}': unknown static code {names}")


def _read(filepath: Optional[Path], marker: str, staticcodemap: StaticCodeMap):
    if filepath and marker:
        begin = re.compile(rf"(?P<indent>\s*).*{marker}\s+BEGIN\s+(?P<name>.+?)\s*")
        info = None

        try:
            with open(filepath, encoding="utf-8") as file:
                fileiter = enumerate(file, 1)
                while True:
                    if info:
                        # process static code
                        _process(filepath, marker, staticcodemap, fileiter, begin, info)
                        info = None
                    else:
                        # normal lines
                        while True:
                            lineno, line = next(fileiter)
                            # search for BEGIN
                            beginmatch = begin.match(line)
                            if beginmatch:
                                # consume BEGIN
                                info = Info(lineno, **beginmatch.groupdict())
                                break

        except (StopIteration, FileNotFoundError):
            pass
        if info:
            raise MakolatorError(f"'{filepath!s}:{info.lineno}' BEGIN without END.")


def _process(filepath: Path, marker: str, staticcodemap: StaticCodeMap, fileiter, begin, info: Info):
    # pylint: disable=too-many-arguments
    end = re.compile(rf"(?P<indent>\s*).*{marker}\s+END\s+(?P<name>.+?)\s*")
    lines: List[str] = []
    while True:
        # search END
        lineno, line = next(fileiter)

        beginmatch = begin.match(line)
        if beginmatch:
            msg = f"missing END tag {info.name!r} for '{filepath!s}:{info.lineno}'"
            raise MakolatorError(msg)

        endmatch = end.match(line)
        if endmatch:
            # consume END
            LOGGER.info("Static Code %r at '%s:%d'", info.name, str(filepath), info.lineno)
            if info.name not in staticcodemap:
                staticcodemap[info.name] = "".join(lines)
            else:
                msg = f"duplicate static code {info.name!r} at '{filepath!s}:{info.lineno}'"
                raise MakolatorError(msg)
            check_indent(filepath, lineno, info.indent, endmatch.group("indent"))
            break
        lines.append(line)
