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
from typing import Generator, List, Optional

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

LOGGER = logging.getLogger(__name__)


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
        with open_(filepath, encoding=encoding, mkdir=True, **kwargs) as file:
            try:
                yield file
            finally:
                file.close()
                if self.config.verbose:
                    print(f"'{filepath!s}'... {file.state.value}")

    def render(self, template_filepaths: List[Path], dest: Optional[Path] = None, context: Optional[dict] = None):
        """
        Render template file.

        Args:
            template_filepaths: Templates.

        Keyword Args:
            dest: Output File.
            context: Key-Value Pairs pairs forwarded to the template.
        """
        LOGGER.debug("render(%r, %r)", [str(filepath) for filepath in template_filepaths], dest)
        templates = self._create_templates(template_filepaths, self.config.template_paths)
        context = context or {}
        if dest is None:
            self._render(next(templates), sys.stdout, None, context)
        else:
            # Mako takes care about proper newline handling. Therefore we deactivate
            # the universal newline mode, by setting newline="".
            with self.open_outputfile(dest, newline="") as output:
                self._render(next(templates), output, dest, context)

    def _render(self, template: Template, output, dest: Optional[Path], context: dict):
        context = Context(output, **self._get_render_context(dest, context))
        template.render_context(context)

    def render_inplace(
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
        LOGGER.debug("render_inplace(%r, %r)", [str(filepath) for filepath in template_filepaths], filepath)
        templates = tuple(self._create_templates(template_filepaths, self.config.template_paths))
        config = self.config
        context = context or {}
        inplace = InplaceRenderer(
            LOGGER, config.template_marker, config.inplace_marker, templates, ignore_unknown, context
        )
        with self.open_outputfile(filepath, existing=Existing.KEEP_TIMESTAMP, newline="") as outputfile:
            context = self._get_render_context(filepath, context or {})
            inplace.render(filepath, outputfile, context)

    def _create_templates(
        self, template_filepaths: List[Path], searchpaths: List[Path]
    ) -> Generator[Template, None, None]:
        filepaths = list(self._find_files(template_filepaths, searchpaths))
        lookuppaths = uniquelist([filepath.parent for filepath in filepaths] + searchpaths)
        lookup = self._create_template_lookup(lookuppaths)
        found = False
        for filepath in filepaths:
            yield lookup.get_template(filepath.name)
            found = True
        if template_filepaths and not found:
            raise MakolatorError(
                f"None of the templates {_humanify(template_filepaths)} found at {_humanify(searchpaths)}."
            )

    def _create_template_lookup(self, searchpaths: List[Path]) -> TemplateLookup:
        cache_path = self.cache_path

        def get_module_filename(filepath: str, uri: str):
            # pylint: disable=unused-argument
            hash_ = hashlib.sha256()
            hash_.update(bytes(filepath, encoding="utf-8"))
            ident = hash_.hexdigest()
            return cache_path / f"{Path(filepath).name}_{ident}.py"

        return TemplateLookup(
            directories=[str(item) for item in searchpaths],
            cache_dir=self.cache_path,
            input_encoding="utf-8",
            output_encoding="utf-8",
            modulename_callable=get_module_filename,
        )

    @staticmethod
    def _find_files(filepaths: List[Path], searchpaths: List[Path]) -> Generator[Path, None, None]:
        """Find `filepath` in `searchpaths` and return first match."""
        for filepath in filepaths:
            if filepath.is_absolute():
                # absolute
                if filepath.exists():
                    yield filepath
            else:
                # relative
                for searchpath in searchpaths:
                    joined = searchpath / filepath
                    if joined.exists():
                        yield joined

    def _get_render_context(self, output_filepath: Optional[Path], context: dict) -> dict:
        result = {
            "datamodel": self.datamodel,
            "output_filepath": output_filepath,
            "render": self.render,
            "render_inplace": self.render_inplace,
        }
        result.update(context)
        return result


def _humanify(iterable):
    if iterable:
        return ", ".join(repr(str(item)) for item in iterable)
    return "''"
