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
"""Makolator Helper."""

import os
import subprocess
import tempfile
from typing import Any


def run(args, **kwargs):
    """
    Run External Command And Use Command STDOUT as Result.

    :any:`subprocess.run` wrapper.
    STDOUT is taken as result.

    The variable ``${TMPDIR}`` in the arguments will be replaced by a temporary directory
    path.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        if isinstance(args, str):
            args = args.replace("${TMPDIR}", tmpdir)
        else:
            args = [arg.replace("${TMPDIR}", tmpdir) for arg in args]
        kwargs["stdout"] = subprocess.PIPE
        result = subprocess.run(args, check=True, **kwargs)  # noqa: S603
        return result.stdout.decode("utf-8").rstrip()


def indent(text_or_int: Any, rstrip: bool = False):
    """
    Indent Lines by number of ``text_or_int``.

        >>> print(indent('''A # doctest: +SKIP
        ... B
        ... C'''))
          A
          B
          C

        >>> print(indent(4)('''A # doctest: +SKIP
        ... B
        ... C'''))
            A
            B
            C
    """
    if isinstance(text_or_int, int):
        return prefix(" " * text_or_int, rstrip=rstrip)
    return prefix("  ", rstrip=rstrip)(text_or_int)


def prefix(pre: str, rstrip: bool = False):
    """
    Add ``pre`` In Front of Every Line.

        >>> print(prefix('PRE-')('''A # doctest: +SKIP
        ... B
        ... C'''))
        PRE-A
        PRE-B
        PRE-C
    """
    if rstrip:

        def func(text):
            return os.linesep.join(f"{pre}{line}".rstrip() for line in text.splitlines())

    else:

        def func(text):
            return os.linesep.join(f"{pre}{line}" for line in text.splitlines())

    return func
