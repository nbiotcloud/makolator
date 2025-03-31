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
"""
The Makolator.

A simple API to an improved Mako.
"""

import hashlib
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from shutil import rmtree
from tempfile import TemporaryFile

from attrs import define, field
from mako.lookup import TemplateLookup
from mako.runtime import Context
from mako.template import Template
from outputfile import Existing, State, open_
from uniquer import uniquelist

from . import escape, helper
from ._inplace import InplaceRenderer
from ._staticcode import StaticCode, read
from ._util import LOGGER, Paths, humanify, iter_files, norm_paths
from .config import Config
from .datamodel import Datamodel
from .exceptions import MakolatorError
from .info import Info
from .tags import Tag
from .tracker import AddState, Tracker

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

    tracker: Tracker = field(factory=Tracker)
    """File Change Tracker."""

    __cache_path: Path | None = None

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

    def remove(self, filepaths: Paths):
        """Remove files or files in given directories."""
        for filepath in iter_files(norm_paths(filepaths)):
            self._remove_file(filepath)

    def _remove_file(self, filepath: Path):
        try:
            filepath.unlink()
            self.tracker.add(filepath, AddState.REMOVED)

        except (PermissionError, FileNotFoundError):
            self.tracker.add(filepath, State.FAILED)

    @contextmanager
    def open_outputfile(self, filepath: Path, encoding: str = "utf-8", **kwargs):
        """
        Open Outputfile and Return Context.

        Args:
            filepath: path of the created/updated file.

        Keyword Args:
            encoding: Charset.
            kwargs: Additional arguments are forwarded to open.

        Example:

            >>> mklt = Makolator(config=Config(verbose=True))
            >>> with mklt.open_outputfile("myfile.txt") as file:
            ...     file.write("data")
            'myfile.txt'... CREATED.
            >>> with mklt.open_outputfile("myfile.txt") as file:
            ...     file.write("data")
            'myfile.txt'... identical. untouched.
        """
        config = self.config
        kwargs.setdefault("existing", config.existing)
        state = State.FAILED
        try:
            with open_(filepath, encoding=encoding, mkdir=True, diffout=self.config.diffout, **kwargs) as file:
                yield file
            state = file.state
        finally:
            if config.track:
                self.tracker.add(filepath, state)
            if config.verbose:
                print(f"'{filepath!s}'... {state.value}")

    def gen(self, template_filepaths: Paths, dest: Path | None = None, context: dict | None = None):
        """
        Render template file.

        Args:
            template_filepaths: Templates.

        Keyword Args:
            dest: Output File.
            context: Key-Value Pairs pairs forwarded to the template.
        """
        template_filepaths = norm_paths(template_filepaths)
        LOGGER.debug("_gen(%r, %r)", [str(filepath) for filepath in template_filepaths], str(dest or "STDOUT"))
        tplfilepaths, lookup = self._create_template_lookup(
            template_filepaths, self.config.template_paths, required=True
        )
        templates = self._create_templates(tplfilepaths, lookup)
        context = context or {}
        comment_sep = self._get_comment_sep(dest)
        if dest is None:
            # newlines may be broken on STDOUT under windows - WON'T FIX
            with TemporaryFile(mode="w+", newline="") as out:
                with read(dest, comment_sep, self.config) as staticcode:
                    template = next(templates)  # Load template
                    LOGGER.info("gen(%r, STDOUT)", template.filename)
                    self._render(template, out, None, context, staticcode, comment_sep)
                out.seek(0)
                for line in out:
                    print(line.rstrip())
        else:
            # Mako takes care about proper newline handling. Therefore we deactivate
            # the universal newline mode, by setting newline="".
            with self.open_outputfile(dest, newline="") as output:
                with read(dest, comment_sep, self.config) as staticcode:
                    template = next(templates)  # Load template
                    LOGGER.info("gen(%r, %r)", template.filename, str(dest))
                    self._render(template, output, dest, context, staticcode, comment_sep)

    def _render(
        self, template: Template, output, dest: Path | None, context: dict, staticcode: StaticCode, comment_sep: str
    ):
        context = Context(output, **self._get_render_context(dest, context, staticcode, comment_sep))
        template.render_context(context)

    def inplace(
        self,
        template_filepaths: Paths,
        filepath: Path,
        context: dict | None = None,
        ignore_unknown: bool = False,
    ):
        """
        Update generated code within `filename` between BEGIN/END markers.

        Args:
            template_filepaths: Templates.
            filepath: File to update.

        Keyword Args:
            context: Key-Value Pairs pairs forwarded to the template.
            ignore_unknown: Ignore unknown inplace markers, instead of raising an error.
        """
        template_filepaths = norm_paths(template_filepaths)
        LOGGER.debug("_inplace(%r, %r)", [str(filepath) for filepath in template_filepaths], str(filepath))
        tplfilepaths, lookup = self._create_template_lookup(template_filepaths, self.config.template_paths)
        templates = tuple(self._create_templates(tplfilepaths, lookup))
        config = self.config
        context = context or {}
        comment_sep = self._get_comment_sep(filepath)
        eol = self._get_eol(filepath, config.inplace_eol_comment)
        inplace = InplaceRenderer(config, templates, ignore_unknown, eol)
        with self.open_outputfile(filepath, existing=Existing.KEEP_TIMESTAMP, newline="") as outputfile:
            with read(filepath, comment_sep, config) as staticcode:
                LOGGER.info("inplace(%r, %r)", str(tplfilepaths[0]) if tplfilepaths else None, str(filepath))
                context = self._get_render_context(filepath, context, staticcode, comment_sep, inplace=True)
                inplace.render(lookup, filepath, outputfile, context)

    def _create_templates(self, tplfilepaths: list[Path], lookup: TemplateLookup) -> Generator[Template, None, None]:
        for tplfilepath in tplfilepaths:
            yield lookup.get_template(tplfilepath.name)
        yield Template(
            """<%! from makolator import helper %>
<%def name="run(*args, **kwargs)">\
${helper.run(*args, **kwargs)}\
</%def>"""
        )

    def _create_template_lookup(
        self, template_filepaths: list[Path], searchpaths: list[Path], required: bool = False
    ) -> tuple[list[Path], TemplateLookup]:
        cache_path = self.cache_path
        tplfilepaths = list(self._find_files(template_filepaths, searchpaths, required=required))
        lookuppaths = uniquelist([tplfilepath.parent for tplfilepath in tplfilepaths] + searchpaths)

        def get_module_filename(filepath: str, uri: str):
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
        filepaths: list[Path], searchpaths: list[Path], required: bool = False
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
            if not searchpaths:
                raise MakolatorError(f"None of the templates {humanify(filepaths)}.")
            raise MakolatorError(f"None of the templates {humanify(filepaths)} found at {humanify(searchpaths)}.")

    def _get_render_context(
        self,
        output_filepath: Path | None,
        context: dict,
        staticcode: StaticCode,
        comment_sep: str,
        inplace: bool = False,
    ) -> dict:
        result = dict(context)
        result.update(HELPER)
        tags = [Tag.GENERATED.value]
        if inplace:
            tags.append(Tag.INPLACE_GENERATED.value)
        elif staticcode.is_volatile:
            tags.append(Tag.FULLY_GENERATED.value)
        result["datamodel"] = self.datamodel
        result["makolator"] = self
        result["output_filepath"] = output_filepath
        result["output_tags"] = tuple(tags)
        result["staticcode"] = staticcode
        result["comment"] = helper.prefix(f"{comment_sep} ", rstrip=True)
        return result

    def _get_comment_sep(self, filepath: Path | None, default: str = "//") -> str:
        if not filepath:
            return default
        return self.config.comment_map.get(filepath.suffix, default)

    def _get_eol(self, filepath: Path, eol_comment: str | None):
        if eol_comment:
            sep = self._get_comment_sep(filepath)
            return f"{sep} {eol_comment}"
        return ""

    def clean(self, filepaths: Paths):
        """Remove Fully-Generated Files from Filepaths."""
        for filepath in iter_files(norm_paths(filepaths)):
            is_fully_generated = self.is_fully_generated(filepath)
            if is_fully_generated:
                self._remove_file(filepath)
            elif is_fully_generated is False:
                self.tracker.add(filepath, State.IDENTICAL)

    def is_fully_generated(self, filepath: Path) -> bool | None:
        """Check If File Is Fully Generated."""
        try:
            with filepath.open("r") as file:
                for _, line in zip(range(self.config.tag_lines), file, strict=False):
                    if Tag.FULLY_GENERATED.value in line:
                        return True
            return False
        except UnicodeDecodeError:  # binary files
            return None
