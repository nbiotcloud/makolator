#
# MIT License
#
# Copyright (c) 2024 nbiotcloud
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
"""Update Tracker."""

from pathlib import Path
from typing import Dict, List, Tuple

from attrs import define, field
from outputfile import State

_STAT_INIT = {
    State.UPDATED: 0,
    State.IDENTICAL: 0,
    State.CREATED: 0,
    State.OVERWRITTEN: 0,
    State.EXISTING: 0,
    State.FAILED: 0,
}


@define
class Tracker:
    """Update Tracker."""

    _items: List[Tuple[Path, State]] = field(factory=list)
    _stat: Dict[State, int] = field(factory=lambda: dict(_STAT_INIT))

    def add(self, path: Path, state: State) -> None:
        """Add Information."""
        self._items.append((path, state))
        self._stat[state] += 1

    def clear(self):
        """Clear Information."""
        self._items.clear()
        self._stat = dict(_STAT_INIT)

    @property
    def total(self):
        """Total Number of Files."""
        return sum(self._stat.values())

    @property
    def stat(self) -> str:
        counts = (f"{count} {state.value}" for state, count in self._stat.items() if count)
        return " ".join((f"{self.total} files.", *counts))
