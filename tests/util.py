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
"""Test Utilities."""
import contextlib
import logging
import os
import re
import shutil
import subprocess

from pytest import approx

LEARN = True

LOGGER = logging.getLogger(__name__)


@contextlib.contextmanager
def chdir(path):
    """Change Working Directory to ``path``."""
    curdir = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(curdir)


def format_output(result, tmp_path=None):
    """Format Command Output."""
    text = result.output
    lines = text.split("\n")
    if tmp_path:
        lines = [replace_path(line, tmp_path, "TMP") for line in lines]
    return lines


def format_logs(caplog, tmp_path=None):
    """Format Logs."""
    lines = [f"{record.levelname:7s} {record.name} {record.message}" for record in caplog.records]
    if tmp_path:
        lines = [replace_path(line, tmp_path, "TMP") for line in lines]
    return lines


def replace_path(text, path, repl):
    """Replace ``path`` by ``repl`` in ``text``."""
    path_esc = re.escape(str(path))
    sep_esc = re.escape(os.path.sep)
    regex = re.compile(rf"{path_esc}([A-Za-z0-9_{sep_esc}]*)")

    def func(mat):
        sub = mat.group(1)
        sub = sub.replace(os.path.sep, "/")
        return f"{repl}{sub}"

    return regex.sub(func, text)


def assert_gen(genpath, refpath, capsys=None, caplog=None, tmp_path=None):
    """Compare Generated Files Versus Reference."""
    genpath.mkdir(parents=True, exist_ok=True)
    refpath.mkdir(parents=True, exist_ok=True)
    if capsys:
        captured = capsys.readouterr()
        out = captured.out
        err = captured.err
        if tmp_path:
            out = replace_path(out, tmp_path, "TMP")
            err = replace_path(err, tmp_path, "TMP")
        (genpath / "stdout.txt").write_text(out)
        (genpath / "stderr.txt").write_text(err)
    if caplog:
        with open(genpath / "logging.txt", "wt", encoding="utf-8") as file:
            for item in format_logs(caplog, tmp_path=tmp_path):
                file.write(f"{item}\n")
    if LEARN:  # pragma: no cover
        logging.getLogger(__name__).warning("LEARNING %s", refpath)
        shutil.rmtree(refpath, ignore_errors=True)
        shutil.copytree(genpath, refpath)
    cmd = ["diff", "-r", "--exclude", "__pycache__", str(refpath), str(genpath)]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as error:  # pragma: no cover
        assert False, error.stdout.decode("utf-8")


def cmp_mtime(mtime0, mtime1):
    """Compare Modification Times"""
    # Hack, to resolve floating round issue
    return abs(mtime1 - mtime0) == approx(0)
