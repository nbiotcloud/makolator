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
"""Makolator Information."""

import pathlib
import shlex
import sys
from typing import Optional

from attrs import define


def get_cli() -> str:
    """Determine Command Line Invocation."""
    argv = sys.argv[:]
    argv[0] = pathlib.Path(argv[0]).name
    return " ".join(shlex.quote(arg) for arg in argv)


@define
class Info:
    """
    Makolator Information.
    """

    # pylint: disable=too-few-public-methods

    cli: Optional[str] = None
    """
    Actual Command Line Interface Call.
    """

    genwarning: str = "THIS FILE IS GENERATED!!! DO NOT EDIT MANUALLY. CHANGES ARE LOST."
    """
    Generated Code Warning.
    """

    inplacewarning: str = "THIS SECTION IS GENERATED!!! DO NOT EDIT MANUALLY. CHANGES ARE LOST."
    """
    Generated Inplace Code Warning.
    """
