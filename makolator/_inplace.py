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
"""Inplace Generation."""
import io
import logging
import re
from pathlib import Path
from typing import Any, List, Optional, Tuple

from attrs import define, field
from mako.exceptions import text_error_template
from mako.lookup import TemplateLookup
from mako.runtime import Context
from mako.template import Template

from .exceptions import MakolatorError

# pylint: disable=too-many-arguments,too-few-public-methods

LOGGER = logging.getLogger("makolator")


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
    lines: List[str] = field(factory=list)


@define
class InplaceRenderer:

    """Inplace Renderer."""

    template_marker: str
    inplace_marker: str
    templates: Tuple[Template, ...]
    ignore_unknown: bool
    context: dict

    def render(self, lookup: TemplateLookup, filepath: Path, outputfile, context: dict):
        """Render."""
        # pylint: disable=too-many-locals,too-many-nested-blocks
        inplace_marker = self.inplace_marker
        ibegin = re.compile(rf"(?P<indent>\s*).*{inplace_marker}\s+BEGIN\s(?P<funcname>[a-z_]+)\((?P<args>.*)\).*")
        iinfo = None

        template_marker = self.template_marker
        tplinfo = None
        tbegin = re.compile(rf"(?P<pre>.*)\s*{template_marker}\s+BEGIN.*")
        templates = list(self.templates)

        with open(filepath, encoding="utf-8") as inputfile:
            inputiter = enumerate(inputfile.readlines(), 1)
            try:
                while True:
                    if iinfo:
                        # GENERATE INPLACE
                        self._process_inplace(filepath, outputfile, context, inputiter, iinfo)
                        iinfo = None

                    elif tplinfo:
                        # MAKO TEMPLATE
                        self._process_template(lookup, outputfile, templates, inputiter, tplinfo)
                        tplinfo = None

                    else:
                        # normal lines
                        while True:
                            lineno, line = next(inputiter)
                            outputfile.write(line)
                            if inplace_marker:
                                # search for "INPLACE BEGIN <funcname>(<args>)"
                                beginmatch = ibegin.match(line)
                                if beginmatch:
                                    # consume INPLACE BEGIN
                                    iinfo = self._start_inplace(templates, filepath, lineno, **beginmatch.groupdict())
                                    break
                            if template_marker:
                                # search for "TEMPLATE BEGIN"
                                beginmatch = tbegin.match(line)
                                if beginmatch:
                                    # consume TEMPLATE BEGIN
                                    tplinfo = TplInfo(lineno, beginmatch.group("pre"))
                                    break

            except StopIteration:
                pass
        if iinfo:
            raise MakolatorError(f"{filepath!s}:{iinfo.lineno} BEGIN {iinfo.funcname}({iinfo.args})' without END.")
        if tplinfo:
            raise MakolatorError(f"{filepath!s}:{tplinfo.lineno} BEGIN without END.")

    def _process_inplace(self, filepath: Path, outputfile, context: dict, inputiter, iinfo):
        while True:
            # search for "INPLACE END <funcname>"
            lineno, line = next(inputiter)

            endmatch = iinfo.end.match(line)
            if endmatch:
                # fill
                self._fill_inplace(filepath, outputfile, iinfo, context)
                # propagate INPLACE END tag
                outputfile.write(line)
                self._check_indent(filepath, lineno, iinfo, endmatch.group("indent"))
                # consume INPLACE END
                break

    def _process_template(self, lookup: TemplateLookup, outputfile, templates, inputiter, tplinfo):
        # capture TEMPLATE
        pre = tplinfo.pre
        prelen = len(pre)
        tend = re.compile(rf"(?P<pre>.*)\s*{self.template_marker}\s+END.*")
        while True:
            _, line = next(inputiter)
            # propagate
            outputfile.write(line)
            # search for "INPLACE END"
            endmatch = tend.match(line)
            if endmatch:
                LOGGER.info("Template '%s:%d'", outputfile, tplinfo.lineno)
                templates.append(Template("".join(tplinfo.lines), lookup=lookup))
                break
            if line.startswith(pre):
                line = line[prelen:]
            tplinfo.lines.append(line)

    def _start_inplace(
        self, templates: List[Template], filepath: Path, lineno: int, indent: str, funcname: str, args: str
    ) -> Optional[InplaceInfo]:
        for template in templates:
            try:
                func = template.get_def(funcname)
            except AttributeError:
                continue
            end = re.compile(rf"(?P<indent>\s*).*{self.inplace_marker}\s+END\s{funcname}.*")
            return InplaceInfo(lineno, indent, funcname, args, func, end)
        if not self.ignore_unknown:
            raise MakolatorError(f"{filepath!s}:{lineno} Function '{funcname}' is not found in templates.")
        return None

    def _check_indent(self, filepath: Path, lineno: int, inplace: InplaceInfo, endindent):
        if endindent != inplace.indent:
            LOGGER.warning(
                "%s:%d Indent of END tag %r does not match indent of BEGIN tag %r.",
                filepath,
                lineno,
                endindent,
                inplace.indent,
            )

    def _fill_inplace(self, filepath: Path, outputfile, inplace: InplaceInfo, context: dict):
        LOGGER.info("Inplace '%s:%d'", filepath, inplace.lineno)
        # determine args, kwargs
        try:
            # pylint: disable=eval-used
            args, kwargs = eval(f"_extract({inplace.args})", {"_extract": _extract})
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
        for line in buffer.getvalue().splitlines():
            if line:
                outputfile.write(f"{indent}{line}\n")
            else:
                outputfile.write("\n")

        buffer.close()


def _extract(*args, **kwargs):
    return (args, kwargs)
