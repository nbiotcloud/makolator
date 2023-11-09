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

from pytest import fixture, raises

from makolator import Config, Makolator, MakolatorError

from .util import assert_gen, assert_paths, cmp_mtime

# pylint: disable=redefined-outer-name


FILEPATH = Path(__file__)
TESTDATA = FILEPATH.parent / "testdata"
REFDATA = FILEPATH.parent / "refdata" / FILEPATH.stem
PAUSE = 0.1


@fixture
def mklt():
    """Default :any:`Makolator` instance with proper ``template_paths``."""
    mklt = Makolator()
    mklt.config.template_paths = [TESTDATA]
    yield mklt


def test_gen_abs(tmp_path, caplog, capsys):
    """Generate File With Absolute Path."""
    mklt = Makolator()
    mklt.gen([TESTDATA / "test.txt.mako"], tmp_path / "test.txt")
    assert_gen(tmp_path, REFDATA / "test_gen_abs", capsys=capsys, caplog=caplog, tmp_path=tmp_path)


def test_gen_abs_template_not_found(tmp_path):
    """Template File With Absolute Path Not Found."""
    mklt = Makolator()
    with raises(MakolatorError, match="None of the templates.*"):
        mklt.gen([TESTDATA / "test.tt.mako"], tmp_path / "test.txt")


def test_gen_rel(tmp_path, caplog, capsys):
    """Generate File With Relative Path."""
    mklt = Makolator(config=Config(template_paths=[TESTDATA]))
    mklt.gen([Path("test.txt.mako")], tmp_path / "test.txt")
    assert_gen(tmp_path, REFDATA / "test_gen_rel", capsys=capsys, caplog=caplog, tmp_path=tmp_path)


def test_gen_rel_sub(tmp_path):
    """Generate File With Relative Path Sub."""
    mklt = Makolator(config=Config(template_paths=[TESTDATA.parent]))
    mklt.gen([Path(TESTDATA.name) / "test.txt.mako"], tmp_path / "test.txt")
    assert_gen(tmp_path, REFDATA / "test_gen_rel_sub")


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
    assert_gen(tmp_path, REFDATA / "test_gen_datamodel")


def test_gen_datamodel_timestamp(tmp_path):
    """Keep Timestamp by Default."""
    mklt = Makolator()
    outfile = tmp_path / "test.txt"
    mklt.gen([TESTDATA / "test.txt.mako"], outfile)

    mtime = outfile.stat().st_mtime

    time.sleep(PAUSE)
    mklt.gen([TESTDATA / "test.txt.mako"], outfile)

    assert cmp_mtime(mtime, outfile.stat().st_mtime)


def test_gen_verbose(tmp_path, mklt, caplog, capsys):
    """Generate File Verbose."""
    mklt.config.verbose = True
    mklt.gen([Path("test.txt.mako")], tmp_path / "test.txt")
    mklt.gen([Path("test.txt.mako")], tmp_path / "test.txt")
    assert_gen(
        tmp_path,
        REFDATA / "test_gen_verbose",
        caplog=caplog,
        capsys=capsys,
        tmp_path=tmp_path,
    )


def test_gen_stdout(tmp_path, mklt, caplog, capsys):
    """Generate File stdout."""
    mklt.gen([Path("test.txt.mako")])
    assert_gen(
        tmp_path,
        REFDATA / "test_gen_stdout",
        caplog=caplog,
        capsys=capsys,
        tmp_path=tmp_path,
    )


def test_gen_context(tmp_path, mklt):
    """Generate File with Context."""
    context = {"myvar": "myvalue"}
    mklt.gen([Path("context.txt.mako")], tmp_path / "context.txt", context=context)
    assert_gen(tmp_path, REFDATA / "test_gen_context")


def test_gen_hier_base(tmp_path, mklt):
    """Generate File Hierarchy - base."""
    mklt.gen([Path("base.txt.mako")], tmp_path / "base.txt")
    assert_gen(tmp_path, REFDATA / "test_gen_hier_base")


def test_gen_hier_impl(tmp_path, mklt):
    """Generate File Hierarchy - impl."""
    mklt.gen([Path("impl.txt.mako")], tmp_path / "impl.txt")
    assert_gen(tmp_path, REFDATA / "test_gen_hier_impl")


def test_gen_run(tmp_path, mklt):
    """Use run()."""
    mklt.gen([Path("run.txt.mako")], tmp_path / "run.txt")
    assert_gen(tmp_path, REFDATA / "test_gen_run")


def test_gen_run_broken(tmp_path, mklt):
    """Use run(), which fails."""
    with raises(FileNotFoundError):
        mklt.gen([Path("run-broken.txt.mako")], tmp_path / "run.txt")


def test_gen_static_create(tmp_path, mklt):
    """Static Code Handling."""
    filepath = tmp_path / "static.txt"
    mklt.gen([Path("static.txt.mako")], filepath)
    assert_gen(tmp_path, REFDATA / "test_gen_static_create")


def test_gen_static(tmp_path, mklt):
    """Static Code Handling."""
    filepath = tmp_path / "static.txt"
    copyfile(TESTDATA / "static.txt", filepath)
    mklt.gen([Path("static.txt.mako")], filepath)
    assert_gen(tmp_path, REFDATA / "test_gen_static")


def test_gen_static_duplicate_tpl(tmp_path, mklt):
    """Static Code Handling With Duplicate In Template."""
    filepath = tmp_path / "static.txt"
    copyfile(TESTDATA / "static.txt", filepath)
    with raises(MakolatorError, match=re.escape("duplicate static code 'a'")):
        mklt.gen([Path("static-duplicate.txt.mako")], filepath)
    assert_paths(TESTDATA / "static.txt", filepath)


def test_gen_static_duplicate(tmp_path, mklt):
    """Static Code Handling With Duplicate In File."""
    filepath = tmp_path / "static.txt"
    copyfile(TESTDATA / "static-duplicate.txt", filepath)
    match = match = re.escape(f"duplicate static code 'a' at '{filepath!s}:6'")
    with raises(MakolatorError, match=match):
        mklt.gen([Path("static.txt.mako")], filepath)
    assert_paths(TESTDATA / "static-duplicate.txt", filepath)


def test_gen_static_noend(tmp_path, mklt):
    """Static Code Handling Without End."""
    filepath = tmp_path / "static.txt"
    copyfile(TESTDATA / "static-noend.txt", filepath)
    match = match = re.escape(f"'{filepath!s}:2' BEGIN without END.")
    with raises(MakolatorError, match=match):
        mklt.gen([Path("static.txt.mako")], filepath)
    assert_paths(TESTDATA / "static-noend.txt", filepath)


def test_gen_static_mixend(tmp_path, mklt):
    """Static Code Handling With Mixed End."""
    filepath = tmp_path / "static.txt"
    copyfile(TESTDATA / "static-mixend.txt", filepath)
    match = match = re.escape(f"missing END tag 'a' for '{filepath!s}:2'")
    with raises(MakolatorError, match=match):
        mklt.gen([Path("static.txt.mako")], filepath)
    assert_paths(TESTDATA / "static-mixend.txt", filepath)


def test_gen_static_unknown(tmp_path, mklt):
    """Static Code Handling With Unknown."""
    filepath = tmp_path / "static.txt"
    copyfile(TESTDATA / "static-unknown.txt", filepath)
    match = match = re.escape(f"'{filepath!s}': unknown static code 'c'")
    with raises(MakolatorError, match=match):
        mklt.gen([Path("static.txt.mako")], filepath)
    assert_paths(TESTDATA / "static-unknown.txt", filepath)


def test_gen_static_corner_create(tmp_path, mklt, caplog):
    """Generate File with Corner Cases."""
    filepath = tmp_path / "static.txt"
    mklt.gen([Path("static-corner.txt.mako")], filepath)
    assert_gen(tmp_path, REFDATA / "test_gen_static_corner_create", caplog=caplog, tmp_path=tmp_path)


def test_gen_static_corner(tmp_path, mklt, caplog):
    """Generate File with Corner Cases."""
    filepath = tmp_path / "static.txt"
    copyfile(TESTDATA / "static-corner.txt", filepath)
    mklt.gen([Path("static-corner.txt.mako")], filepath)
    assert_gen(tmp_path, REFDATA / "test_gen_static_corner", caplog=caplog, tmp_path=tmp_path)
