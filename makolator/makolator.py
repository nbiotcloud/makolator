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
"""
The Makolator.

A simple API to an improved Mako.
"""

import hashlib
import logging
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from shutil import rmtree
from typing import Generator, List, Optional, Tuple

from attrs import define, field
from mako.lookup import TemplateLookup
from mako.runtime import Context
from mako.template import Template
from outputfile import Existing, open_
from uniquer import uniquelist

from . import escape, helper
from ._inplace import InplaceRenderer
from ._staticcode import StaticCode, read
from ._util import Paths, humanify, norm_paths
from .config import Config
from .datamodel import Datamodel
from .exceptions import MakolatorError
from .info import Info

LOGGER = logging.getLogger("makolator")

HELPER = {
    "indent": helper.indent,
    "prefix": helper.prefix,
    "run": helper.run,
    "tex": escape.tex,
}


@define
class Makolator:
    """
    The Makolator.

    A simple API to an improved http://www.makotemplates.org/
    """

    config: Config = field(factory=Config)
    """The Configuration."""

    datamodel: Datamodel = field(factory=Datamodel)
    """The Data Container."""

    info: Info = field(factory=Info)
    """Makolator Information."""

    __cache_path: Optional[Path] = None

    def __del__(self):
        if self.__cache_path:
            rmtree(self.__cache_path)
            self.__cache_path = None

    @property
    def cache_path(self) -> Path:
        """Cache Path."""
        cache_path = self.config.cache_path
        if cache_path:
            cache_path.mkdir(parents=True, exist_ok=True)
            return cache_path

        if not self.__cache_path:
            self.__cache_path = Path(tempfile.mkdtemp(prefix="makolator"))
        return self.__cache_path

    @contextmanager
    def open_outputfile(self, filepath: Path, encoding: str = "utf-8", **kwargs):
        """
        Open Outputfile and Return Context.

        Args:
            filepath: path of the created/updated file.

        Keyword Args:
            encoding: Charset.

        >>> mklt = Makolator(config=Config(verbose=True))
        >>> with mklt.open_outputfile("myfile.txt") as file:
        ...     file.write("data")
        'myfile.txt'... CREATED.
        >>> with mklt.open_outputfile("myfile.txt") as file:
        ...     file.write("data")
        'myfile.txt'... identical. untouched.
        """
        with open_(filepath, encoding=encoding, mkdir=True, diffout=self.config.diffout, **kwargs) as file:
            yield file
        if self.config.verbose:
            print(f"'{filepath!s}'... {file.state.value}")

    def gen(self, template_filepaths: Paths, dest: Optional[Path] = None, context: Optional[dict] = None):
        """
        Render template file.

        Args:
            template_filepaths: Templates.

        Keyword Args:
            dest: Output File.
            context: Key-Value Pairs pairs forwarded to the template.
        """
        template_filepaths = norm_paths(template_filepaths)
        LOGGER.debug("gen(%r, %r)", [str(filepath) for filepath in template_filepaths], dest)
        tplfilepaths, lookup = self._create_template_lookup(
            template_filepaths, self.config.template_paths, required=True
        )
        templates = self._create_templates(tplfilepaths, lookup)
        context = context or {}
        comment_sep = self._get_comment_sep(dest)
        if dest is None:
            with read(dest, comment_sep, self.config.static_marker) as staticcode:
                self._render(next(templates), sys.stdout, None, context, staticcode)
        else:
            # Mako takes care about proper newline handling. Therefore we deactivate
            # the universal newline mode, by setting newline="".
            with self.open_outputfile(dest, newline="") as output:
                with read(dest, comment_sep, self.config.static_marker) as staticcode:
                    template = next(templates)  # Load template
                    LOGGER.info("Generate '%s'", dest)
                    self._render(template, output, dest, context, staticcode)

    def _render(self, template: Template, output, dest: Optional[Path], context: dict, staticcode: StaticCode):
        # pylint: disable=too-many-arguments
        context = Context(output, **self._get_render_context(dest, context, staticcode))
        template.render_context(context)

    def inplace(
        self,
        template_filepaths: Paths,
        filepath: Path,
        context: Optional[dict] = None,
        ignore_unknown: bool = False,
    ):
        """
        Update generated code within `filename` between BEGIN/END markers.

        Args:
            template_filepaths: Templates.
            dest: File to update.

        Keyword Args:
            context: Key-Value Pairs pairs forwarded to the template.
            ignore_unknown: Ignore unknown inplace markers, instead of raising an error.
        """
        template_filepaths = norm_paths(template_filepaths)
        LOGGER.debug("inplace(%r, %r)", [str(filepath) for filepath in template_filepaths], filepath)
        tplfilepaths, lookup = self._create_template_lookup(template_filepaths, self.config.template_paths)
        templates = tuple(self._create_templates(tplfilepaths, lookup))
        config = self.config
        context = context or {}
        comment_sep = self._get_comment_sep(filepath)
        eol = self._get_eol(filepath, config.inplace_eol_comment)
        inplace = InplaceRenderer(config.template_marker, config.inplace_marker, templates, ignore_unknown, eol)
        with self.open_outputfile(filepath, existing=Existing.KEEP_TIMESTAMP, newline="") as outputfile:
            with read(filepath, comment_sep, config.static_marker) as staticcode:
                context = self._get_render_context(filepath, context, staticcode)
                inplace.render(lookup, filepath, outputfile, context)

    def _create_templates(self, tplfilepaths: List[Path], lookup: TemplateLookup) -> Generator[Template, None, None]:
        for tplfilepath in tplfilepaths:
            LOGGER.info("Template '%s'", tplfilepath)
            yield lookup.get_template(tplfilepath.name)
        yield Template(
            """<%! from makolator import helper %>
<%def name="run(*args, **kwargs)">\
${helper.run(*args, **kwargs)}\
</%def>"""
        )

    def _create_template_lookup(
        self, template_filepaths: List[Path], searchpaths: List[Path], required: bool = False
    ) -> Tuple[List[Path], TemplateLookup]:
        cache_path = self.cache_path
        tplfilepaths = list(self._find_files(template_filepaths, searchpaths, required=required))
        lookuppaths = uniquelist([tplfilepath.parent for tplfilepath in tplfilepaths] + searchpaths)

        def get_module_filename(filepath: str, uri: str):
            # pylint: disable=unused-argument
            hash_ = hashlib.sha256()
            hash_.update(bytes(filepath, encoding="utf-8"))
            ident = hash_.hexdigest()
            return cache_path / f"{Path(filepath).name}_{ident}.py"

        lookup = TemplateLookup(
            directories=[str(item) for item in lookuppaths],
            cache_dir=self.cache_path,
            input_encoding="utf-8",
            output_encoding="utf-8",
            modulename_callable=get_module_filename,
            strict_undefined=True,
        )
        return tplfilepaths, lookup

    @staticmethod
    def _find_files(
        filepaths: List[Path], searchpaths: List[Path], required: bool = False
    ) -> Generator[Path, None, None]:
        """Find `filepath` in `searchpaths` and return first match."""
        found = False
        for filepath in filepaths:
            if filepath.is_absolute():
                # absolute
                if filepath.exists():
                    yield filepath
                    found = True
            else:
                # relative
                for searchpath in searchpaths:
                    joined = searchpath / filepath
                    if joined.exists():
                        yield joined
                        found = True
        if not found and required:
            raise MakolatorError(f"None of the templates {humanify(filepaths)} found at {humanify(searchpaths)}.")

    def _get_render_context(self, output_filepath: Optional[Path], context: dict, staticcode: StaticCode) -> dict:
        result = dict(context)
        result.update(HELPER)
        result["datamodel"] = self.datamodel
        result["makolator"] = self
        result["output_filepath"] = output_filepath
        result["staticcode"] = staticcode
        return result

    def _get_comment_sep(self, filepath: Optional[Path], default="//"):
        if not filepath:
            return default
        return self.config.comment_map.get(filepath.suffix, default)

    def _get_eol(self, filepath: Path, eol_comment: Optional[str]):
        if eol_comment:
            sep = self._get_comment_sep(filepath)
            return f"{sep} {eol_comment}"
        return ""
