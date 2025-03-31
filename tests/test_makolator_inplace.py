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
"""Makolator Testing."""

import re
from pathlib import Path
from shutil import copyfile

from mako.exceptions import CompileException
from pytest import fixture, raises
from test2ref import assert_paths, assert_refdata

from makolator import Makolator, MakolatorError

FILEPATH = Path(__file__)
TESTDATA = FILEPATH.parent / "testdata"
REFDATA = FILEPATH.parent / "refdata" / FILEPATH.stem


@fixture
def mklt():
    """Default :any:`Makolator` instance with proper ``template_paths``."""
    mklt = Makolator()
    mklt.config.template_paths = [TESTDATA]
    yield mklt


def test_inplace(tmp_path, capsys, caplog):
    """Render File Inplace."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace.txt", filepath)
    mklt = Makolator()
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_refdata(test_inplace, tmp_path, capsys=capsys, caplog=caplog)


def test_disabled(tmp_path, capsys, caplog):
    """Render File Inplace."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace.txt", filepath)
    mklt = Makolator()
    mklt.config.template_marker = None
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_refdata(test_disabled, tmp_path, capsys=capsys, caplog=caplog)


def test_indent(tmp_path, caplog):
    """Render File Inplace Indent."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-indent.txt", filepath)
    mklt = Makolator()
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_refdata(test_indent, tmp_path, caplog=caplog)


def test_broken_arg(tmp_path):
    """Rarger File Inplace with broken arg."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-broken-arg.txt", filepath)
    mklt = Makolator()
    with raises(MakolatorError, match=re.escape(r"SyntaxError")):
        mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)


def test_broken_end(tmp_path):
    """Render File Inplace with broken end."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-broken-end.txt", filepath)
    mklt = Makolator()
    with raises(MakolatorError, match=re.escape(r"without END.")):
        mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)


def test_broken_func(tmp_path):
    """Render File Inplace with broken gen."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-broken-gen.txt", filepath)
    mklt = Makolator()
    with raises(MakolatorError, match=re.escape(r"ZeroDivisionError: division by zero")):
        mklt.inplace([TESTDATA / "inplace-broken-func.txt.mako"], filepath)


def test_unknown(tmp_path):
    """Render File Inplace with missing func."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-unknown.txt", filepath)
    mklt = Makolator()
    with raises(MakolatorError, match=re.escape(r"Function 'bfunc' is not found in template")):
        mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)


def test_unknown_ignore(tmp_path):
    """Render File Inplace with missing func."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-unknown.txt", filepath)
    mklt = Makolator()
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath, ignore_unknown=True)
    assert_refdata(test_unknown_ignore, tmp_path)


def test_child(tmp_path):
    """Render File Inplace with missing func."""
    filepath = tmp_path / "inplace-child.txt"
    copyfile(TESTDATA / "inplace-child.txt", filepath)
    mklt = Makolator()
    mklt.inplace([TESTDATA / "inplace-child.txt.mako"], filepath, ignore_unknown=True)
    assert_refdata(test_child, tmp_path)


def test_mako_only(tmp_path):
    """Render File Inplace with mako."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-tpl.txt", filepath)
    mklt = Makolator()
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_refdata(test_mako_only, tmp_path)


def test_mako_disabled(tmp_path):
    """Render File Inplace with mako."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-tpl.txt", filepath)
    mklt = Makolator()
    mklt.config.inplace_marker = None
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)


def test_mako_broken(tmp_path):
    """Render File Inplace with mako."""
    filepath = tmp_path / "inplace.txt"
    inpfilepath = TESTDATA / "inplace-tpl-broken.txt"
    copyfile(inpfilepath, filepath)
    mklt = Makolator()
    with raises(MakolatorError, match=re.escape(" BEGIN without END.")):
        mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)

    assert filepath.read_text(encoding="utf-8") == inpfilepath.read_text(encoding="utf-8")


def test_mako_broken2(tmp_path):
    """Render File Inplace with mako."""
    filepath = tmp_path / "inplace.txt"
    inpfilepath = TESTDATA / "inplace-tpl-broken2.txt"
    copyfile(inpfilepath, filepath)
    mklt = Makolator()
    with raises(CompileException, match=re.escape("Fragment")):
        mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert filepath.read_text(encoding="utf-8") == inpfilepath.read_text(encoding="utf-8")


def test_eol(tmp_path):
    """Render File Inplace Indent."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-simple.txt", filepath)
    mklt = Makolator()
    mklt.config.inplace_eol_comment = "GENERATED"
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_refdata(test_eol, tmp_path)


def test_eol_sv(tmp_path):
    """Render File Inplace Indent - SystemVerilog."""
    filepath = tmp_path / "inplace.sv"
    copyfile(TESTDATA / "inplace-simple.txt", filepath)
    mklt = Makolator()
    mklt.config.inplace_eol_comment = "GENERATED"
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_refdata(test_eol_sv, tmp_path)


def test_eol_cpp(tmp_path):
    """Render File Inplace Indent - C++."""
    filepath = tmp_path / "inplace.cpp"
    copyfile(TESTDATA / "inplace-simple.txt", filepath)
    mklt = Makolator()
    mklt.config.inplace_eol_comment = "GENERATED"
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_refdata(test_eol_cpp, tmp_path)


def test_eol_ini(tmp_path):
    """Render File Inplace Indent - Ini."""
    filepath = tmp_path / "inplace.ini"
    copyfile(TESTDATA / "inplace-simple.txt", filepath)
    mklt = Makolator()
    mklt.config.inplace_eol_comment = "GENERATED"
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_refdata(test_eol_ini, tmp_path)


def test_run(tmp_path):
    """Render File Inplace run."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-run.txt", filepath)
    mklt = Makolator()
    mklt.inplace([], filepath)
    assert_refdata(test_run, tmp_path)


def test_run_broken(tmp_path):
    """Render File Inplace run."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-run-broken.txt", filepath)
    mklt = Makolator()
    with raises(MakolatorError):
        mklt.inplace([], filepath)
    assert_paths(TESTDATA / "inplace-run-broken.txt", filepath)


def test_noend(tmp_path, mklt):
    """Render File Inplace with no end."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-noend.txt", filepath)
    with raises(MakolatorError, match=re.escape(f"'{filepath}:2' BEGIN afunc('foo')) without END.")):
        mklt.inplace([Path("inplace.txt.mako")], filepath)
    assert_paths(TESTDATA / "inplace-noend.txt", filepath)


def test_mixend(tmp_path, mklt):
    """Render File Inplace with mixed end."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-mixend.txt", filepath)
    with raises(MakolatorError, match=re.escape(f"missing END tag 'afunc' for '{filepath!s}:2'")):
        mklt.inplace([Path("inplace.txt.mako")], filepath)
    assert_paths(TESTDATA / "inplace-mixend.txt", filepath)


def test_mako_noend(tmp_path, mklt):
    """Render File Mako with no end."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-mako-noend.txt", filepath)
    with raises(MakolatorError, match=re.escape(f"'{filepath!s}:2' BEGIN without END.")):
        mklt.inplace([Path("inplace.txt.mako")], filepath)
    assert_paths(TESTDATA / "inplace-mako-noend.txt", filepath)


def test_mako_mixend(tmp_path, mklt):
    """Render File Mako with mixed end."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-mako-mixend.txt", filepath)
    with raises(MakolatorError, match=re.escape(f"missing END tag for '{filepath!s}:2'")):
        mklt.inplace([Path("inplace.txt.mako")], filepath)
    assert_paths(TESTDATA / "inplace-mako-mixend.txt", filepath)


def test_helper(tmp_path, mklt):
    """Generate File with Helper."""
    filepath = tmp_path / "helper.txt"
    copyfile(TESTDATA / "helper.txt", filepath)
    mklt.inplace([Path("helper.txt.mako")], filepath)
    assert_refdata(test_helper, tmp_path)


def test_inplace_nofill(tmp_path):
    """Render File Inplace with ffill."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-fill.txt", filepath)
    mklt = Makolator()
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_refdata(test_inplace_nofill, tmp_path)


def test_inplace_fill(tmp_path):
    """Render File Inplace with ffill."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-fill.txt", filepath)
    mklt = Makolator()
    mklt.config.marker_linelength = 80
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_refdata(test_inplace_fill, tmp_path)


def test_inplace_fillstar(tmp_path):
    """Render File Inplace with ffill."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-fill.txt", filepath)
    mklt = Makolator()
    mklt.config.marker_fill = "*"
    mklt.config.marker_linelength = 40
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_refdata(test_inplace_fillstar, tmp_path)


def test_mako_only_nofill(tmp_path):
    """Render File Inplace with mako."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-tpl-fill.txt", filepath)
    mklt = Makolator()
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_refdata(test_mako_only_nofill, tmp_path)


def test_mako_only_fill(tmp_path):
    """Render File Inplace with mako."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-tpl-fill.txt", filepath)
    mklt = Makolator()
    mklt.config.marker_linelength = 80
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_refdata(test_mako_only_fill, tmp_path)


def test_mako_only_fillstar(tmp_path):
    """Render File Inplace with mako."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-tpl-fill.txt", filepath)
    mklt = Makolator()
    mklt.config.marker_fill = "*"
    mklt.config.marker_linelength = 40
    mklt.inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_refdata(test_mako_only_fillstar, tmp_path)
