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
import time
from pathlib import Path

from pytest import raises

from makolator import Config, Makolator, MakolatorError

from .util import assert_gen, cmp_mtime

TESTDATA = Path(__file__).parent / "testdata"
PAUSE = 0.1


def test_gen_abs(tmp_path, caplog, capsys):
    """Generate File With Absolute Path."""
    mklt = Makolator()
    mklt.gen([TESTDATA / "test.txt.mako"], tmp_path / "test.txt")
    assert_gen(
        tmp_path, TESTDATA / "test_makolator_gen" / "test_gen_abs", capsys=capsys, caplog=caplog, tmp_path=tmp_path
    )


def test_gen_abs_template_not_found(tmp_path):
    """Template File With Absolute Path Not Found."""
    mklt = Makolator()
    with raises(MakolatorError, match="None of the templates.*"):
        mklt.gen([TESTDATA / "test.tt.mako"], tmp_path / "test.txt")


def test_gen_rel(tmp_path, caplog, capsys):
    """Generate File With Relative Path."""
    mklt = Makolator(config=Config(template_paths=[TESTDATA]))
    mklt.gen([Path("test.txt.mako")], tmp_path / "test.txt")
    assert_gen(
        tmp_path, TESTDATA / "test_makolator_gen" / "test_gen_rel", capsys=capsys, caplog=caplog, tmp_path=tmp_path
    )


def test_gen_rel_sub(tmp_path):
    """Generate File With Relative Path Sub."""
    mklt = Makolator(config=Config(template_paths=[TESTDATA.parent]))
    mklt.gen([Path(TESTDATA.name) / "test.txt.mako"], tmp_path / "test.txt")
    assert_gen(tmp_path, TESTDATA / "test_makolator_gen" / "test_gen_rel_sub")


def test_gen_rel_sub_not_found(tmp_path):
    """Generate File With Relative Path Sub."""
    mklt = Makolator(config=Config(template_paths=[TESTDATA.parent]))
    with raises(MakolatorError, match="None of the templates.*"):
        mklt.gen([Path(TESTDATA.name) / "test.tt.mako"], tmp_path / "test.txt")


def test_gen_datamodel(tmp_path):
    """Use Datamodel Statement In Templates."""
    mklt = Makolator()
    mklt.datamodel.item = "myitem"
    mklt.gen([TESTDATA / "test.txt.mako"], tmp_path / "test.txt")
    assert_gen(tmp_path, TESTDATA / "test_makolator_gen" / "test_gen_datamodel")


def test_gen_datamodel_timestamp(tmp_path):
    """Keep Timestamp by Default."""
    mklt = Makolator()
    outfile = tmp_path / "test.txt"
    mklt.gen([TESTDATA / "test.txt.mako"], outfile)

    mtime = outfile.stat().st_mtime

    time.sleep(PAUSE)
    mklt.gen([TESTDATA / "test.txt.mako"], outfile)

    assert cmp_mtime(mtime, outfile.stat().st_mtime)


def test_gen_verbose(tmp_path, caplog, capsys):
    """Generate File Verbose."""
    mklt = Makolator()
    mklt.config.template_paths = [TESTDATA]
    mklt.config.verbose = True
    mklt.gen([Path("test.txt.mako")], tmp_path / "test.txt")
    mklt.gen([Path("test.txt.mako")], tmp_path / "test.txt")
    assert_gen(
        tmp_path,
        TESTDATA / "test_makolator_gen" / "test_gen_verbose",
        caplog=caplog,
        capsys=capsys,
        tmp_path=tmp_path,
    )


def test_gen_stdout(tmp_path, caplog, capsys):
    """Generate File stdout."""
    mklt = Makolator()
    mklt.config.template_paths = [TESTDATA]
    mklt.gen([Path("test.txt.mako")])
    assert_gen(
        tmp_path,
        TESTDATA / "test_makolator_gen" / "test_gen_stdout",
        caplog=caplog,
        capsys=capsys,
        tmp_path=tmp_path,
    )


def test_gen_context(tmp_path):
    """Generate File with Context."""
    mklt = Makolator()
    context = {"myvar": "myvalue"}
    mklt.gen([TESTDATA / "context.txt.mako"], tmp_path / "context.txt", context=context)
    assert_gen(tmp_path, TESTDATA / "test_makolator_gen" / "test_gen_context")


def test_gen_hier_base(tmp_path):
    """Generate File Hierarchy - base."""
    mklt = Makolator()
    mklt.config.template_paths = [TESTDATA]
    mklt.gen([Path("base.txt.mako")], tmp_path / "base.txt")
    assert_gen(tmp_path, TESTDATA / "test_makolator_gen" / "test_gen_hier_base")


def test_gen_hier_impl(tmp_path):
    """Generate File Hierarchy - impl."""
    mklt = Makolator()
    mklt.config.template_paths = [TESTDATA]
    mklt.gen([Path("impl.txt.mako")], tmp_path / "impl.txt")
    assert_gen(tmp_path, TESTDATA / "test_makolator_gen" / "test_gen_hier_impl")
