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
"""Tracker Testing."""

from contextlib_chdir import chdir
from pytest import mark, raises
from test2ref import assert_refdata

from makolator import Config, Existing, Makolator


@mark.parametrize("existing", [Existing.KEEP, Existing.KEEP_TIMESTAMP, Existing.OVERWRITE, Existing.ERROR])
@mark.parametrize("update", ["content", "change"])
def test_tracker(tmp_path, capsys, existing, update):
    """Test Tracker."""
    mkl = Makolator(config=Config(verbose=True, existing=existing, track=True))
    with chdir(tmp_path):
        with mkl.open_outputfile("file.txt") as file:
            file.write("content")

        if existing == Existing.ERROR:
            with raises(FileExistsError):
                with mkl.open_outputfile("file.txt") as file:
                    file.write(update)
        else:
            with mkl.open_outputfile("file.txt") as file:
                file.write(update)

        with raises(RuntimeError):
            with mkl.open_outputfile("exc.txt"):
                raise RuntimeError

    tracker = mkl.tracker
    assert tracker.total == 3
    assert tracker.created == 1
    assert tracker.updated == (1 if update == "change" and existing == Existing.KEEP_TIMESTAMP else 0)
    assert tracker.identical == (1 if update == "content" and existing == Existing.KEEP_TIMESTAMP else 0)
    assert tracker.overwritten == (1 if existing == Existing.OVERWRITE else 0)
    assert tracker.identical == (1 if update == "content" and existing == Existing.KEEP_TIMESTAMP else 0)
    assert tracker.existing == (1 if existing == Existing.KEEP else 0)
    assert tracker.failed == (2 if existing == Existing.ERROR else 1)

    print(tracker.stat)

    assert_refdata(test_tracker, tmp_path, capsys=capsys, flavor=f"{existing.value}-{update}")


def test_clear(tmp_path):
    """Explicit Tracker Clear."""
    mkl = Makolator()
    mkl.config.track = True
    with chdir(tmp_path):
        with mkl.open_outputfile("file.txt") as file:
            file.write("content")

    assert mkl.tracker.stat == "1 files. 1 CREATED."
    mkl.tracker.clear()
    assert mkl.tracker.stat == "0 files."
