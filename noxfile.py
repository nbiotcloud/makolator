#
# MIT License
#
# Copyright (c) 2024 nbiotcloud
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

"""
NOX Configuration.

See [NOX Documentation](https://nox.thea.codes/en/stable/) for further details
"""

import os
import pathlib

import nox

os.environ.update(
    {
        "PDM_IGNORE_SAVED_PYTHON": "1",
        "LANGUAGE": "en_US",
    }
)
nox.options.sessions = ["format", "test", "checkdeps", "checktypes", "doc"]
nox.options.reuse_existing_virtualenvs = True

IS_DEV = bool(int(os.environ.get("DEV", "0")))
PYTHON = False if IS_DEV else None
PDM_VERSION = "2.22.0"


@nox.session(python=PYTHON)
def format(session: nox.Session) -> None:
    """Run Code Formatter and Checks."""
    if not IS_DEV:
        session.run_install("pip", "install", f"pdm=={PDM_VERSION}")
        session.run_install("pdm", "install", "-G", "format")
    session.run("pre-commit", "run", "--all-files")


@nox.session(python=PYTHON)
def test(session: nox.Session) -> None:
    """Run Test - Additional Arguments are forwarded to `pytest`."""
    if not IS_DEV:
        session.run_install("pip", "install", f"pdm=={PDM_VERSION}")
        session.run_install("pdm", "install", "-G", "test")
    session.run("pytest", "-vv", *session.posargs)
    htmlcovfile = pathlib.Path().resolve() / "htmlcov" / "index.html"
    print(f"Coverage report:\n\n    file://{htmlcovfile!s}\n")


@nox.session(python=PYTHON)
def checkdeps(session: nox.Session) -> None:
    """Check Dependencies."""
    if not IS_DEV:
        session.run_install("pip", "install", f"pdm=={PDM_VERSION}")
        session.run_install("pdm", "install")
    session.run("python", "-c", "import makolator")


@nox.session(python=PYTHON)
def checktypes(session: nox.Session) -> None:
    """Run Type Checks."""
    if not IS_DEV:
        session.run_install("pip", "install", f"pdm=={PDM_VERSION}")
        session.run_install("pdm", "install", "-G", "checktypes")
    session.run("mypy", "src", "tests")


@nox.session(python=PYTHON)
def doc(session: nox.Session) -> None:
    """Build Documentation."""
    if not IS_DEV:
        session.run_install("pip", "install", f"pdm=={PDM_VERSION}")
        session.run_install("pdm", "install", "-G", "doc")
    session.run("make", "html", "-C", "docs")
    docindexfile = pathlib.Path().resolve() / "docs" / "build" / "html" / "index.html"
    print(f"Documentation is available at:\n\n    file://{docindexfile!s}\n")


@nox.session()
def dev(session: nox.Session) -> None:
    """Development Environment  - Additional Arguments Are Executed."""
    session.run_install("pip", "install", f"pdm=={PDM_VERSION}")
    session.run_install("pdm", "install", "-G", ":all")
    session.run("pip", "install", "-e", ".")
    if session.posargs:
        session.run(*session.posargs, external=True, env={"DEV": "1"})