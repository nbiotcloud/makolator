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

from makolator import Config, Existing

COMMENT_MAP = {
    ".c": "//",
    ".c++": "//",
    ".cpp": "//",
    ".ini": "#",
    ".py": "#",
    ".sv": "//",
    ".svh": "//",
    ".tex": "%",
    ".txt": "//",
    ".v": "//",
    ".vh": "//",
}


def test_config():
    """Basic Testing on Config."""
    config = Config()

    assert not config.template_paths
    assert config.existing == Existing.KEEP_TIMESTAMP
    assert config.diffout is None
    assert config.verbose is False
    assert config.inplace_eol_comment is None
    assert config.comment_map == COMMENT_MAP
    assert config.inplace_marker == "GENERATE INPLACE"
    assert config.template_marker == "MAKO TEMPLATE"
    assert config.static_marker == "STATIC"


def test_config_modified():
    """Modified Configuration."""
    config = Config(
        template_paths=[Path("foo"), Path("bar")],
        existing=Existing.KEEP,
        diffout=print,
        verbose=True,
        inplace_marker="INP",
        template_marker="TPL",
        static_marker="STAT",
    )

    assert config.template_paths == [Path("foo"), Path("bar")]
    assert config.existing == Existing.KEEP
    assert config.diffout is print
    assert config.verbose is True
    assert config.inplace_eol_comment is None
    assert config.comment_map == COMMENT_MAP
    assert config.inplace_marker == "INP"
    assert config.template_marker == "TPL"
    assert config.static_marker == "STAT"
