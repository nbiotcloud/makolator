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
"""Makolator Testing."""
from pathlib import Path

from makolator import Makolator

from .util import assert_gen

FILEPATH = Path(__file__)
TESTDATA = FILEPATH.parent / "testdata"
REFDATA = FILEPATH.parent / "refdata" / FILEPATH.stem


def test_makolator_main(tmp_path, caplog, capsys):
    """."""
    mkl = Makolator()
    mkl.config.template_paths = [TESTDATA]
    mkl.gen(Path("main.txt.mako"), tmp_path / "main.txt")
    assert_gen(
        tmp_path,
        REFDATA / "test_makolator_main",
        capsys=capsys,
        caplog=caplog,
        tmp_path=tmp_path,
    )
