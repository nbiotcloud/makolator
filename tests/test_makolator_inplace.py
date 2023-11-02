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
import re
from pathlib import Path
from shutil import copyfile

from mako.exceptions import CompileException
from pytest import raises

from makolator import Makolator, MakolatorError

from .util import assert_gen

TESTDATA = Path(__file__).parent / "testdata"


def test_inplace(tmp_path, capsys, caplog):
    """Render File Inplace."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace.txt", filepath)
    mklt = Makolator()
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_gen(
        tmp_path, TESTDATA / "test_makolator_inplace" / "test_inplace", capsys=capsys, caplog=caplog, tmp_path=tmp_path
    )


def test_inplace_disabled(tmp_path, capsys, caplog):
    """Render File Inplace."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace.txt", filepath)
    mklt = Makolator()
    mklt.config.template_marker = None
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_gen(
        tmp_path,
        TESTDATA / "test_makolator_inplace" / "test_inplace_disabled",
        capsys=capsys,
        caplog=caplog,
        tmp_path=tmp_path,
    )


def test_inplace_indent(tmp_path, caplog):
    """Render File Inplace Indent."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-indent.txt", filepath)
    mklt = Makolator()
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_gen(tmp_path, TESTDATA / "test_makolator_inplace" / "test_inplace_indent", caplog=caplog, tmp_path=tmp_path)


def test_inplace_broken_arg(tmp_path):
    """Rarger File Inplace with broken arg."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-broken-arg.txt", filepath)
    mklt = Makolator()
    with raises(MakolatorError, match=re.escape(r"SyntaxError")):
        mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)


def test_inplace_broken_end(tmp_path):
    """Render File Inplace with broken end."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-broken-end.txt", filepath)
    mklt = Makolator()
    with raises(MakolatorError, match=re.escape(r"without END.")):
        mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)


def test_inplace_broken_func(tmp_path):
    """Render File Inplace with broken gen."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-broken-gen.txt", filepath)
    mklt = Makolator()
    with raises(MakolatorError, match=re.escape(r"ZeroDivisionError: division by zero")):
        mklt.inplace([TESTDATA / "inplace-broken-func.txt.mako"], filepath)


def test_inplace_unknown(tmp_path):
    """Render File Inplace with missing func."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-unknown.txt", filepath)
    mklt = Makolator()
    with raises(MakolatorError, match=re.escape(r"Function 'bfunc' is not found in template")):
        mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)


def test_inplace_unknown_ignore(tmp_path):
    """Render File Inplace with missing func."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-unknown.txt", filepath)
    mklt = Makolator()
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath, ignore_unknown=True)
    assert_gen(tmp_path, TESTDATA / "test_makolator_inplace" / "test_inplace_unknown_ignore")


def test_inplace_child(tmp_path):
    """Render File Inplace with missing func."""
    filepath = tmp_path / "inplace-child.txt"
    copyfile(TESTDATA / "inplace-child.txt", filepath)
    mklt = Makolator()
    mklt.inplace([TESTDATA / "inplace-child.txt.mako"], filepath, ignore_unknown=True)
    assert_gen(tmp_path, TESTDATA / "test_makolator_inplace" / "test_inplace_child")


def test_inplace_mako_only(tmp_path):
    """Render File Inplace with mako."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-tpl.txt", filepath)
    mklt = Makolator()
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_gen(tmp_path, TESTDATA / "test_makolator_inplace" / "test_inplace_mako_only")


def test_inplace_mako_disabled(tmp_path):
    """Render File Inplace with mako."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-tpl.txt", filepath)
    mklt = Makolator()
    mklt.config.inplace_marker = None
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)


def test_inplace_mako_broken(tmp_path):
    """Render File Inplace with mako."""
    filepath = tmp_path / "inplace.txt"
    inpfilepath = TESTDATA / "inplace-tpl-broken.txt"
    copyfile(inpfilepath, filepath)
    mklt = Makolator()
    with raises(MakolatorError, match=re.escape(" BEGIN without END.")):
        mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)

    assert filepath.read_text(encoding="utf-8") == inpfilepath.read_text(encoding="utf-8")


def test_inplace_mako_broken2(tmp_path):
    """Render File Inplace with mako."""
    filepath = tmp_path / "inplace.txt"
    inpfilepath = TESTDATA / "inplace-tpl-broken2.txt"
    copyfile(inpfilepath, filepath)
    mklt = Makolator()
    with raises(CompileException, match=re.escape("Fragment")):
        mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert filepath.read_text(encoding="utf-8") == inpfilepath.read_text(encoding="utf-8")


def test_inplace_eol(tmp_path):
    """Render File Inplace Indent."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-simple.txt", filepath)
    mklt = Makolator()
    mklt.config.inplace_eol_comment = "GENERATED"
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_gen(tmp_path, TESTDATA / "test_makolator_inplace" / "test_inplace_eol", tmp_path=tmp_path)


def test_inplace_eol_sv(tmp_path):
    """Render File Inplace Indent - SystemVerilog."""
    filepath = tmp_path / "inplace.sv"
    copyfile(TESTDATA / "inplace-simple.txt", filepath)
    mklt = Makolator()
    mklt.config.inplace_eol_comment = "GENERATED"
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_gen(tmp_path, TESTDATA / "test_makolator_inplace" / "test_inplace_eol_sv", tmp_path=tmp_path)


def test_inplace_eol_cpp(tmp_path):
    """Render File Inplace Indent - C++."""
    filepath = tmp_path / "inplace.cpp"
    copyfile(TESTDATA / "inplace-simple.txt", filepath)
    mklt = Makolator()
    mklt.config.inplace_eol_comment = "GENERATED"
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_gen(tmp_path, TESTDATA / "test_makolator_inplace" / "test_inplace_eol_cpp", tmp_path=tmp_path)


def test_inplace_eol_ini(tmp_path):
    """Render File Inplace Indent - Ini."""
    filepath = tmp_path / "inplace.ini"
    copyfile(TESTDATA / "inplace-simple.txt", filepath)
    mklt = Makolator()
    mklt.config.inplace_eol_comment = "GENERATED"
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_gen(tmp_path, TESTDATA / "test_makolator_inplace" / "test_inplace_eol_ini", tmp_path=tmp_path)
