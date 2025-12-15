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

from pytest import fixture

from makolator import Config, Makolator

FILEPATH = Path(__file__)
TESTDATA = FILEPATH.parent / "testdata"
PAUSE = 0.1


@fixture
def tracker():
    """Tracker."""
    return []


@fixture
def pre_post(tracker):
    """Pre."""

    def pre_create(filepath):
        tracker.append(("pre_create", filepath))

    def post_create(filepath):
        tracker.append(("post_create", filepath))

    def pre_update(filepath):
        tracker.append(("pre_update", filepath))

    def post_update(filepath):
        tracker.append(("post_update", filepath))

    def pre_remove(filepath):
        tracker.append(("pre_remove", filepath))

    def post_remove(filepath):
        tracker.append(("post_remove", filepath))

    return {
        "pre_create": pre_create,
        "post_create": post_create,
        "pre_update": pre_update,
        "post_update": post_update,
        "pre_remove": pre_remove,
        "post_remove": post_remove,
    }


@fixture
def mklt(pre_post):
    """Default :any:`Makolator` instance with proper ``template_paths``."""
    config = Config(template_paths=[TESTDATA], **pre_post)
    yield Makolator(config=config)


def test_gen(tmp_path, mklt, tracker):
    """Test Generate."""
    mklt.datamodel.name = "some-name"  # type: ignore[attr-defined]
    gen_path = tmp_path / "gen"
    mklt.gen([TESTDATA / "gen-recursive"], gen_path)
    assert tracker == [
        ("pre_create", gen_path / "some-name.txt"),
        ("post_create", gen_path / "some-name.txt"),
        ("pre_create", gen_path / "empty.txt"),
        ("post_create", gen_path / "empty.txt"),
        ("pre_create", gen_path / "file.txt"),
        ("post_create", gen_path / "file.txt"),
        ("pre_create", gen_path / "sub/file.txt"),
        ("post_create", gen_path / "sub/file.txt"),
        ("pre_create", gen_path / "templated.txt"),
        ("post_create", gen_path / "templated.txt"),
        ("pre_create", gen_path / "test.xlsx"),
        ("post_create", gen_path / "test.xlsx"),
    ]
    tracker.clear()

    mklt.gen([TESTDATA / "gen-recursive"], gen_path)
    assert tracker == []

    mklt.datamodel.name = "other-name"  # type: ignore[attr-defined]
    mklt.gen([TESTDATA / "gen-recursive"], gen_path)
    assert tracker == [
        ("pre_create", gen_path / "other-name.txt"),
        ("post_create", gen_path / "other-name.txt"),
        ("pre_update", gen_path / "templated.txt"),
        ("post_update", gen_path / "templated.txt"),
    ]
    tracker.clear()

    mklt.clean([gen_path / "some-name.txt"])
    assert tracker == [
        ("pre_remove", gen_path / "some-name.txt"),
        ("post_remove", gen_path / "some-name.txt"),
    ]
    tracker.clear()
