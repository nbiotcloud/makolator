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

from pathlib import Path

from contextlib_chdir import chdir

from makolator import Config, Datamodel, Existing, Makolator, Tracker

FILEPATH = Path(__file__)
TESTDATA = FILEPATH.parent / "testdata"


def test_makolator():
    """Basic Testing On Makolator."""
    mkl = Makolator()
    assert mkl.config == Config()
    assert mkl.datamodel == Datamodel()
    assert mkl.tracker == Tracker()


def test_outputfile(tmp_path, capsys):
    """Test Outputfile."""
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
    assert mkl.tracker.total == 0


def test_outputfile_keep(tmp_path, capsys):
    """Test Outputfile With Keep."""
    mkl = Makolator()
    mkl.config.existing = Existing.KEEP
    with chdir(tmp_path):
        with mkl.open_outputfile("file.txt") as file:
            file.write("content")
        assert file.state.name == "CREATED"
        with mkl.open_outputfile("file.txt") as file:
            file.write("change")
        assert file.state.name == "EXISTING"

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
    assert mkl.tracker.total == 0


def test_create_dir(tmp_path):
    """Create Output Directory Structure If It Does Not Exist."""
    mklt = Makolator()
    outfile = tmp_path / "sub" / "test.txt"
    mklt.gen([TESTDATA / "test.txt.mako"], outfile)


def test_cachepath_default(tmp_path):
    """Default Cache Path."""
    mklt = Makolator()
    cachepath = mklt.cache_path
    assert cachepath.exists()
    assert len(tuple(cachepath.glob("*"))) == 0
    mklt.gen([TESTDATA / "test.txt.mako"], tmp_path / "test.txt")


def test_cachepath_explicit(tmp_path):
    """Explicit Cache Path."""
    mklt = Makolator(config=Config(cache_path=tmp_path / "cache"))
    cachepath = mklt.cache_path
    assert cachepath.exists()
    assert len(tuple(cachepath.glob("*"))) == 0
    mklt.gen([TESTDATA / "test.txt.mako"], tmp_path / "test.txt")
