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
import time
from pathlib import Path
from shutil import copyfile

from pytest import raises

from makolator import Config, Datamodel, Existing, Makolator, MakolatorError

from .util import assert_gen, chdir, cmp_mtime

TESTDATA = Path(__file__).parent / "testdata"
PAUSE = 0.1


def test_makolator():
    """Basic Testing On Makolator."""
    mkl = Makolator()
    assert mkl.config == Config()
    assert mkl.datamodel == Datamodel()


def test_outputfile(tmp_path, capsys):
    """Test Outputfile"""
    mkl = Makolator()
    with chdir(tmp_path):
        with mkl.open_outputfile("file.txt") as file:
            file.write("content")
        assert file.state.name == "CREATED"
        with mkl.open_outputfile("file.txt") as file:
            file.write("change")
        assert file.state.name == "UPDATED"

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_outputfile_keep(tmp_path, capsys):
    """Test Outputfile With Keep"""
    mkl = Makolator()
    mkl.config.existing = Existing.KEEP
    with chdir(tmp_path):
        with mkl.open_outputfile("file.txt") as file:
            file.write("content")
        assert file.state.name == "CREATED"
        with mkl.open_outputfile("file.txt") as file:
            file.write("change")
        assert file.state.name == "UPDATED"

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_render_abs(tmp_path):
    """Render File With Absolute Path."""
    mklt = Makolator()
    mklt.render([TESTDATA / "test.txt.mako"], tmp_path / "test.txt")
    assert_gen(tmp_path, TESTDATA / "test_makolator" / "test_render_abs")


def test_render_abs_template_not_found(tmp_path):
    """Template File With Absolute Path Not Found."""
    mklt = Makolator()
    with raises(MakolatorError, match="None of the templates.*"):
        mklt.render([TESTDATA / "test.tt.mako"], tmp_path / "test.txt")


def test_render_rel(tmp_path):
    """Render File With Relative Path."""
    mklt = Makolator(config=Config(template_paths=[TESTDATA]))
    mklt.render([Path("test.txt.mako")], tmp_path / "test.txt")
    assert_gen(tmp_path, TESTDATA / "test_makolator" / "test_render_rel")


def test_render_rel_sub(tmp_path):
    """Render File With Relative Path Sub."""
    mklt = Makolator(config=Config(template_paths=[TESTDATA.parent]))
    mklt.render([Path(TESTDATA.name) / "test.txt.mako"], tmp_path / "test.txt")
    assert_gen(tmp_path, TESTDATA / "test_makolator" / "test_render_rel_sub")


def test_render_rel_sub_not_found(tmp_path):
    """Render File With Relative Path Sub."""
    mklt = Makolator(config=Config(template_paths=[TESTDATA.parent]))
    with raises(MakolatorError, match="None of the templates.*"):
        mklt.render([Path(TESTDATA.name) / "test.tt.mako"], tmp_path / "test.txt")


def test_render_datamodel(tmp_path):
    """Use Datamodel Statement In Templates."""
    mklt = Makolator()
    mklt.datamodel.item = "myitem"
    mklt.render([TESTDATA / "test.txt.mako"], tmp_path / "test.txt")
    assert_gen(tmp_path, TESTDATA / "test_makolator" / "test_render_datamodel")


def test_render_datamodel_timestamp(tmp_path):
    """Keep Timestamp by Default."""
    mklt = Makolator()
    outfile = tmp_path / "test.txt"
    mklt.render([TESTDATA / "test.txt.mako"], outfile)

    mtime = outfile.stat().st_mtime

    time.sleep(PAUSE)
    mklt.render([TESTDATA / "test.txt.mako"], outfile)

    assert cmp_mtime(mtime, outfile.stat().st_mtime)


def test_create_dir(tmp_path):
    """Create Output Directory Structure If It Does Not Exist."""
    mklt = Makolator()
    outfile = tmp_path / "sub" / "test.txt"
    mklt.render([TESTDATA / "test.txt.mako"], outfile)


def test_cachepath_default(tmp_path):
    """Default Cache Path."""
    mklt = Makolator()
    cachepath = mklt.cache_path
    assert cachepath.exists()
    assert len(tuple(cachepath.glob("*"))) == 0
    mklt.render([TESTDATA / "test.txt.mako"], tmp_path / "test.txt")


def test_cachepath_explicit(tmp_path):
    """Explicit Cache Path."""
    mklt = Makolator(config=Config(cache_path=tmp_path / "cache"))
    cachepath = mklt.cache_path
    assert cachepath.exists()
    assert len(tuple(cachepath.glob("*"))) == 0
    mklt.render([TESTDATA / "test.txt.mako"], tmp_path / "test.txt")


def test_render_verbose(tmp_path, caplog, capsys):
    """Render File Verbose."""
    mklt = Makolator()
    mklt.config.template_paths = [TESTDATA]
    mklt.config.verbose = True
    mklt.render([Path("test.txt.mako")], tmp_path / "test.txt")
    mklt.render([Path("test.txt.mako")], tmp_path / "test.txt")
    assert_gen(
        tmp_path,
        TESTDATA / "test_makolator" / "test_render_verbose",
        caplog=caplog,
        capsys=capsys,
        tmp_path=tmp_path,
    )


def test_render_stdout(tmp_path, caplog, capsys):
    """Render File stdout."""
    mklt = Makolator()
    mklt.config.template_paths = [TESTDATA]
    mklt.render([Path("test.txt.mako")])
    assert_gen(
        tmp_path,
        TESTDATA / "test_makolator" / "test_render_stdout",
        caplog=caplog,
        capsys=capsys,
        tmp_path=tmp_path,
    )


def test_render_context(tmp_path):
    """Render File with Context."""
    mklt = Makolator()
    context = {"myvar": "myvalue"}
    mklt.render([TESTDATA / "context.txt.mako"], tmp_path / "context.txt", context=context)
    assert_gen(tmp_path, TESTDATA / "test_makolator" / "test_render_context")


def test_render_hier_base(tmp_path):
    """Render File Hierarchy - base."""
    mklt = Makolator()
    mklt.config.template_paths = [TESTDATA]
    mklt.render([Path("base.txt.mako")], tmp_path / "base.txt")
    assert_gen(tmp_path, TESTDATA / "test_makolator" / "test_render_hier_base")


def test_render_hier_impl(tmp_path):
    """Render File Hierarchy - impl."""
    mklt = Makolator()
    mklt.config.template_paths = [TESTDATA]
    mklt.render([Path("impl.txt.mako")], tmp_path / "impl.txt")
    assert_gen(tmp_path, TESTDATA / "test_makolator" / "test_render_hier_impl")


def test_render_inplace(tmp_path):
    """Render File Inplace."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace.txt", filepath)
    mklt = Makolator()
    mklt.render_inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_gen(tmp_path, TESTDATA / "test_makolator" / "test_render_inplace")


def test_render_inplace_indent(tmp_path, caplog):
    """Render File Inplace Indent."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-indent.txt", filepath)
    mklt = Makolator()
    mklt.render_inplace([TESTDATA / "inplace.txt.mako"], filepath)
    assert_gen(tmp_path, TESTDATA / "test_makolator" / "test_render_inplace_indent", caplog=caplog, tmp_path=tmp_path)


def test_render_inplace_broken_arg(tmp_path):
    """Rarger File Inplace with broken arg."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-broken-arg.txt", filepath)
    mklt = Makolator()
    with raises(MakolatorError, match=re.escape(r"SyntaxError")):
        mklt.render_inplace([TESTDATA / "inplace.txt.mako"], filepath)


def test_render_inplace_broken_end(tmp_path):
    """Render File Inplace with broken end."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-broken-end.txt", filepath)
    mklt = Makolator()
    with raises(MakolatorError, match=re.escape(r"without END tag.")):
        mklt.render_inplace([TESTDATA / "inplace.txt.mako"], filepath)


def test_render_inplace_broken_render(tmp_path):
    """Render File Inplace with broken render."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-broken-render.txt", filepath)
    mklt = Makolator()
    with raises(MakolatorError, match=re.escape(r"ZeroDivisionError: division by zero")):
        mklt.render_inplace([TESTDATA / "inplace.txt.mako"], filepath)


def test_render_inplace_unknown(tmp_path):
    """Render File Inplace with missing func."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-unknown.txt", filepath)
    mklt = Makolator()
    with raises(MakolatorError, match=re.escape(r"Function 'bfunc' is not found in template")):
        mklt.render_inplace([TESTDATA / "inplace.txt.mako"], filepath)


def test_render_inplace_unknown_ignore(tmp_path):
    """Render File Inplace with missing func."""
    filepath = tmp_path / "inplace.txt"
    copyfile(TESTDATA / "inplace-unknown.txt", filepath)
    mklt = Makolator()
    mklt.render_inplace([TESTDATA / "inplace.txt.mako"], filepath, ignore_unknown=True)
    assert_gen(tmp_path, TESTDATA / "test_makolator" / "test_render_inplace_unknown_ignore")


def test_render_inplace_child(tmp_path):
    """Render File Inplace with missing func."""
    filepath = tmp_path / "inplace-child.txt"
    copyfile(TESTDATA / "inplace-child.txt", filepath)
    mklt = Makolator()
    mklt.render_inplace([TESTDATA / "inplace-child.txt.mako"], filepath, ignore_unknown=True)
    assert_gen(tmp_path, TESTDATA / "test_makolator" / "test_render_inplace_child")
