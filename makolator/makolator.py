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

from ._inplace import InplaceRenderer
from .config import Config
from .datamodel import Datamodel
from .exceptions import MakolatorError

LOGGER = logging.getLogger("makolator")


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
            try:
                yield file
            finally:
                file.close()
                if self.config.verbose:
                    print(f"'{filepath!s}'... {file.state.value}")

    def gen(self, template_filepaths: List[Path], dest: Optional[Path] = None, context: Optional[dict] = None):
        """
        Render template file.

        Args:
            template_filepaths: Templates.

        Keyword Args:
            dest: Output File.
            context: Key-Value Pairs pairs forwarded to the template.
        """
        LOGGER.debug("gen(%r, %r)", [str(filepath) for filepath in template_filepaths], dest)
        tplfilepaths, lookup = self._create_template_lookup(
            template_filepaths, self.config.template_paths, required=True
        )
        templates = self._create_templates(tplfilepaths, lookup)
        context = context or {}
        if dest is None:
            self._render(next(templates), sys.stdout, None, context)
        else:
            # Mako takes care about proper newline handling. Therefore we deactivate
            # the universal newline mode, by setting newline="".
            with self.open_outputfile(dest, newline="") as output:
                template = next(templates)  # Load template
                LOGGER.info("Generate '%s'", dest)
                self._render(template, output, dest, context)

    def _render(self, template: Template, output, dest: Optional[Path], context: dict):
        context = Context(output, **self._get_render_context(dest, context))
        template.render_context(context)

    def inplace(
        self,
        template_filepaths: List[Path],
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
        LOGGER.debug("inplace(%r, %r)", [str(filepath) for filepath in template_filepaths], filepath)
        tplfilepaths, lookup = self._create_template_lookup(template_filepaths, self.config.template_paths)
        templates = tuple(self._create_templates(tplfilepaths, lookup))
        config = self.config
        context = context or {}
        inplace = InplaceRenderer(config.template_marker, config.inplace_marker, templates, ignore_unknown, context)
        with self.open_outputfile(filepath, existing=Existing.KEEP_TIMESTAMP, newline="") as outputfile:
            context = self._get_render_context(filepath, context or {})
            inplace.render(lookup, filepath, outputfile, context)

    def _create_templates(self, tplfilepaths: List[Path], lookup: TemplateLookup) -> Generator[Template, None, None]:
        for tplfilepath in tplfilepaths:
            LOGGER.info("Template '%s'", tplfilepath)
            yield lookup.get_template(tplfilepath.name)

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
            raise MakolatorError(f"None of the templates {_humanify(filepaths)} found at {_humanify(searchpaths)}.")

    def _get_render_context(self, output_filepath: Optional[Path], context: dict) -> dict:
        result = {
            "datamodel": self.datamodel,
            "output_filepath": output_filepath,
            "gen": self.gen,
            "inplace": self.inplace,
        }
        result.update(context)
        return result


def _humanify(iterable):
    if iterable:
        return ", ".join(repr(str(item)) for item in iterable)
    return "''"
