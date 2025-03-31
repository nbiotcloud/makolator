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
"""Inplace Generation."""

import io
import os
import re
from pathlib import Path
from typing import Any

from aligntext import Align
from attrs import define, field
from mako.exceptions import text_error_template
from mako.lookup import TemplateLookup
from mako.runtime import Context
from mako.template import Template

from ._util import LOGGER, check_indent, fill_marker
from .config import Config
from .exceptions import MakolatorError


@define
class InplaceInfo:
    """Inplace Rendering Context Information."""

    lineno: int
    indent: str
    funcname: str
    args: str
    func: Any
    end: Any


@define
class TplInfo:
    """Template Context Information."""

    lineno: int
    pre: str
    lines: list[str] = field(factory=list)


@define
class InplaceRenderer:
    """Inplace Renderer."""

    config: Config
    templates: tuple[Template, ...]
    ignore_unknown: bool
    eol: str

    def render(self, lookup: TemplateLookup, filepath: Path, outputfile, context: dict):  # noqa: C901
        """Render."""
        inplace_marker = self.config.inplace_marker
        ibegin = re.compile(rf"(?P<indent>\s*).*{inplace_marker}\s+BEGIN\s(?P<funcname>[a-z_]+)\((?P<args>.*)\)")
        iinfo = None

        template_marker = self.config.template_marker
        tinfo = None
        tbegin = re.compile(rf"(?P<pre>.*)\s*{template_marker}\s+BEGIN")
        templates = list(self.templates)

        with filepath.open(encoding="utf-8", newline="") as inputfile:
            inputiter = enumerate(inputfile.readlines(), 1)
            try:
                while True:
                    if iinfo:
                        # GENERATE INPLACE
                        self._process_inplace(filepath, outputfile, context, inputiter, iinfo, ibegin)
                        iinfo = None

                    elif tinfo:
                        # MAKO TEMPLATE
                        self._process_template(filepath, lookup, outputfile, templates, inputiter, tinfo, tbegin)
                        tinfo = None

                    else:
                        # normal lines
                        while True:
                            lineno, line = next(inputiter)
                            if inplace_marker:
                                # search for "INPLACE BEGIN <funcname>(<args>)"
                                beginmatch = ibegin.match(line)
                                if beginmatch:
                                    outputfile.write(self._fill_marker(beginmatch))
                                    # consume INPLACE BEGIN
                                    iinfo = self._start_inplace(templates, filepath, lineno, **beginmatch.groupdict())
                                    break
                            if template_marker:
                                # search for "TEMPLATE BEGIN"
                                beginmatch = tbegin.match(line)
                                if beginmatch:
                                    outputfile.write(self._fill_marker(beginmatch))
                                    # consume TEMPLATE BEGIN
                                    tinfo = TplInfo(lineno, beginmatch.group("pre"))
                                    break
                            outputfile.write(line)

            except StopIteration:
                pass
        if iinfo:
            raise MakolatorError(f"'{filepath!s}:{iinfo.lineno}' BEGIN {iinfo.funcname}({iinfo.args}) without END.")
        if tinfo:
            raise MakolatorError(f"'{filepath!s}:{tinfo.lineno}' BEGIN without END.")

    def _process_inplace(self, filepath: Path, outputfile, context: dict, inputiter, iinfo, ibegin):
        while True:
            # search for "INPLACE END"
            lineno, line = next(inputiter)

            beginmatch = ibegin.match(line)
            if beginmatch:
                msg = f"missing END tag {iinfo.funcname!r} for '{filepath!s}:{iinfo.lineno}'"
                raise MakolatorError(msg)

            endmatch = iinfo.end.match(line)
            if endmatch:
                # fill
                self._fill_inplace(filepath, outputfile, iinfo, context)
                # propagate INPLACE END tag
                outputfile.write(self._fill_marker(endmatch))
                check_indent(filepath, lineno, iinfo.indent, endmatch.group("indent"))
                # consume INPLACE END
                break

    def _process_template(
        self, filepath: Path, lookup: TemplateLookup, outputfile, templates, inputiter, tinfo, tbegin
    ):
        # capture TEMPLATE
        pre = tinfo.pre
        prelen = len(pre)
        tend = re.compile(rf"(?P<pre>.*)\s*{self.config.template_marker}\s+END")
        while True:
            _, line = next(inputiter)

            beginmatch = tbegin.match(line)
            if beginmatch:
                msg = f"missing END tag for '{filepath!s}:{tinfo.lineno}'"
                raise MakolatorError(msg)

            # search for "INPLACE END"
            endmatch = tend.match(line)
            if endmatch:
                outputfile.write(self._fill_marker(endmatch))
                LOGGER.debug("Template '%s:%d'", str(outputfile), tinfo.lineno)
                templates.append(Template("".join(tinfo.lines), lookup=lookup))
                break
            # propagate
            outputfile.write(line)

            if line.startswith(pre):
                line = line[prelen:]
            tinfo.lines.append(line)

    def _start_inplace(
        self, templates: list[Template], filepath: Path, lineno: int, indent: str, funcname: str, args: str
    ) -> InplaceInfo | None:
        for template in templates:
            try:
                func = template.get_def(funcname)
            except AttributeError:
                continue
            end = re.compile(rf"(?P<indent>\s*).*{self.config.inplace_marker}\s+END\s{funcname}")
            return InplaceInfo(lineno, indent, funcname, args, func, end)
        if not self.ignore_unknown:
            raise MakolatorError(f"{filepath!s}:{lineno} Function '{funcname}' is not found in templates.")
        return None

    def _fill_inplace(self, filepath: Path, outputfile, inplace: InplaceInfo, context: dict):
        LOGGER.debug("Inplace '%s:%d'", str(filepath), inplace.lineno)
        # determine args, kwargs
        try:
            args, kwargs = eval(f"_extract({inplace.args})", {"_extract": _extract})  # noqa: S307
        except Exception as exc:
            raise MakolatorError(
                f"{filepath!s}:{inplace.lineno} Function invocation failed. "
                f"{exc!r} in arguments: '{inplace.funcname}({inplace.args})'."
            ) from exc

        # run func(args, kwargs)
        buffer = io.StringIO()
        indent = inplace.indent
        context = Context(buffer, **context)
        try:
            inplace.func.render_context(context, *args, **kwargs)
        except Exception as exc:
            debug = str(text_error_template().render())
            raise MakolatorError(
                f"{filepath!s}:{inplace.lineno} Function '{inplace.funcname}' invocation failed. {exc!r}. {debug}"
            ) from exc
        eol = self.eol
        lines = buffer.getvalue().splitlines()
        linesep = os.linesep
        if eol:
            align = Align()
            for line in lines:
                align.add_row(line, eol)
            for item in align:
                outputfile.write(f"{indent}{item}{linesep}")
        else:
            for line in lines:
                if line:
                    outputfile.write(f"{indent}{line}{linesep}")
                else:
                    outputfile.write(linesep)

        buffer.close()

    def _fill_marker(self, mat: re.Match) -> str:
        marker_fill = self.config.marker_fill
        marker_linelength = self.config.marker_linelength
        if marker_fill and marker_linelength:
            line = mat.string[mat.start() : mat.end()]
            return fill_marker(line, marker_fill, marker_linelength) + os.linesep
        return mat.string


def _extract(*args, **kwargs):
    return (args, kwargs)
