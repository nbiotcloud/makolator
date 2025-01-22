#
# MIT License
#
# Copyright (c) 2025 nbiotcloud
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
"""Info Testing."""

from pytest import fixture

from makolator import Makolator
from makolator._util import iter_files


@fixture
def example(tmp_path):
    """Example File Structure."""
    onedir = tmp_path / "one"
    onedir.mkdir()
    twodir = onedir / "two"
    twodir.mkdir()
    # File without @generated tag
    (onedir / "one.txt").write_text("""
Hello World
""")
    # Two generated files
    (tmp_path / "sec.txt").write_text("""
// @fully-generated
""")
    (tmp_path / "third.txt").write_text("""
// @generated
""")
    # @fully-generated tag out of reach
    with (twodir / "four.txt").open("w") as file:
        for _ in range(100):
            file.write("@fully-generated")
    (onedir / "file.bin").write_bytes(bytes(range(256)))
    yield tmp_path


def test_find_files(example):
    """Find Files."""
    assert tuple(iter_files((example,))) == (
        example / "one" / "file.bin",
        example / "one" / "one.txt",
        example / "one" / "two" / "four.txt",
        example / "sec.txt",
        example / "third.txt",
    )


def test_clean(example):
    """Clean Operation."""
    mklt = Makolator()
    onefile = example / "one" / "one.txt"
    secfile = example / "sec.txt"
    thirdfile = example / "third.txt"
    fourfile = example / "one" / "two" / "four.txt"

    mklt.clean(example)

    assert onefile.exists()
    assert not secfile.exists()
    assert thirdfile.exists()
    assert not fourfile.exists()

    assert mklt.tracker.stat == "4 files. 2 identical. untouched. 2 REMOVED."


def test_remove_files(example):
    """Remove Files."""
    mklt = Makolator()
    onefile = example / "one" / "one.txt"
    secfile = example / "sec.txt"
    thirdfile = example / "third.txt"
    fourfile = example / "one" / "two" / "four.txt"

    mklt.remove(onefile)

    assert not onefile.exists()
    assert secfile.exists()
    assert thirdfile.exists()
    assert fourfile.exists()

    assert mklt.tracker.stat == "1 files. 1 REMOVED."


def test_remove(example):
    """Remove Directories."""
    mklt = Makolator()
    onefile = example / "one" / "one.txt"
    secfile = example / "sec.txt"
    thirdfile = example / "third.txt"
    fourfile = example / "one" / "two" / "four.txt"

    mklt.remove(example / "one")

    assert not onefile.exists()
    assert secfile.exists()
    assert thirdfile.exists()
    assert not fourfile.exists()

    assert mklt.tracker.stat == "3 files. 3 REMOVED."


def test_remove_failed(example):
    """Remove Failed."""
    mklt = Makolator()
    onefile = example / "one" / "one.txt"

    onefile.unlink()
    mklt._remove_file(onefile)

    assert mklt.tracker.stat == "1 files. 1 FAILED."
