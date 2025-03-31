#
# MIT License
#
# Copyright (c) 2023-2025 nbiotcloud
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

import os
import re
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from attrs import define, field

from ._util import LOGGER, check_indent, fill_marker, humanify
from .config import Config
from .exceptions import MakolatorError

StaticCodeMap = dict[str, str]


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
    staticcodemap: StaticCodeMap
    marker: str
    marker_fill: str = ""
    marker_linelength: int = 0

    _names: list[str] = field(factory=list)

    def __call__(self, name, default=None, comment_sep=None):
        if name in self._names:
            raise MakolatorError(f"duplicate static code {name!r}")
        self._names.append(name)
        if comment_sep is None:
            comment_sep = self.comment_sep or ""
        code = self.staticcodemap.pop(name, default) or ""
        cpre = f"{comment_sep} " if comment_sep else ""
        begin = f"{cpre}{self.marker} BEGIN {name}"
        end = f"{cpre}{self.marker} END {name}"
        if self.marker_fill and self.marker_linelength:
            begin = fill_marker(begin, self.marker_fill, self.marker_linelength)
            end = fill_marker(end, self.marker_fill, self.marker_linelength)
        lines = [begin]
        lines.extend(code.splitlines())
        lines.append(end)
        return os.linesep.join(lines)

    @property
    def is_volatile(self) -> bool:
        """Static Code is Empty."""
        return not self.staticcodemap


@contextmanager
def read(filepath: Path | None, comment_sep: str, config: Config) -> Iterator[StaticCode]:
    """Read from ``filepath``."""
    staticcodemap: StaticCodeMap = {}
    marker = config.static_marker
    _read(filepath, marker, staticcodemap)
    yield StaticCode(comment_sep, staticcodemap, marker, config.marker_fill, config.marker_linelength)
    if staticcodemap:
        names = humanify(staticcodemap)
        raise MakolatorError(f"'{filepath!s}': unknown static code {names}")


def _read(filepath: Path | None, marker: str, staticcodemap: StaticCodeMap):
    if filepath and marker:
        begin = re.compile(rf"(?P<indent>\s*).*{marker}\s+BEGIN\s+(?P<name>\S+)\s*")
        info = None

        try:
            with filepath.open(encoding="utf-8", newline="") as file:
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
    end = re.compile(rf"(?P<indent>\s*).*{marker}\s+END\s+(?P<name>\S+)\s*")
    lines: list[str] = []
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
            LOGGER.debug("Static Code %r at '%s:%d'", info.name, str(filepath), info.lineno)
            if info.name not in staticcodemap:
                staticcodemap[info.name] = "".join(lines)
            else:
                msg = f"duplicate static code {info.name!r} at '{filepath!s}:{info.lineno}'"
                raise MakolatorError(msg)
            check_indent(filepath, lineno, info.indent, endmatch.group("indent"))
            break
        lines.append(line)
