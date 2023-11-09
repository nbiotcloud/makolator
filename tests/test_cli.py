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
"""Datamodel Testing."""

from pathlib import Path
from shutil import copyfile

from makolator.cli import main

from .util import assert_gen

FILEPATH = Path(__file__)
TESTDATA = FILEPATH.parent / "testdata"
REFDATA = FILEPATH.parent / "refdata" / FILEPATH.stem


def test_gen(tmp_path):
    """Gen."""
    main(["gen", str(TESTDATA / "test.txt.mako"), str(tmp_path / "test.txt")])
    assert_gen(tmp_path, REFDATA / "test_gen")


def test_inplace(tmp_path):
    """Inplace."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace.txt", filepath)
    main(["inplace", str(TESTDATA / "inplace.txt.mako"), str(filepath)])
    assert_gen(tmp_path, REFDATA / "test_inplace")
