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
from typing import List, Optional

from attrs import define
from mako.exceptions import TemplateLookupException
from mako.lookup import TemplateLookup
from mako.runtime import Context
from mako.template import Template
from outputfile import open_

from .config import Config
from .datamodel import Datamodel
from .exceptions import MakolatorError

LOGGER = logging.getLogger(__name__)


@define
class Makolator:
    """
    The Makolator.

    A simple API to an improved _Mako.

    .. _Mako: http://www.makotemplates.org/
    """

    config: Config = Config()
    datamodel: Datamodel = Datamodel()

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

    def render(self, template_filepaths, dest: Optional[Path] = None, context: Optional[dict] = None):
        """
        Render template file.

        Args:
            template_filepaths: Templates.

        Keyword Args:
            dest: Output File.
            context: Key-Value Pairs pairs forwarded to the template.
        """
        template_paths = self.config.template_paths
        with self._handle_render_exceptions(template_paths):
            template = self._create_template_from_filepaths(template_filepaths, template_paths)
        with self._handle_render_exceptions([Path(item) for item in template.lookup.directories]):
            if dest is None:
                self._render(template, sys.stdout, context=context)
            else:
                # Mako takes care about proper newline handling. Therefore we deactivate
                # the universal newline mode, by setting newline="".
                with self.open_outputfile(dest, newline="") as output:
                    self._render(template, output, dest, context=context)

    def _render(self, template: Template, output, dest: Optional[Path] = None, context: Optional[dict] = None):
        LOGGER.debug("_render(%r, %r)", template.filename, dest)
        context = Context(output, **self._get_context_dict(dest, context=context))
        template.render_context(context)

    def _create_template_from_str(self, searchpaths: List[Path], template: Optional[str] = None) -> Template:
        if template is None:
            template = sys.stdin.read()
        lookup = self._create_template_lookup(searchpaths)
        return Template(template, lookup=lookup)

    def _create_template_from_filepaths(self, template_filepaths: List[Path], searchpaths: List[Path]) -> Template:
        searchpaths = [filepath.parent for filepath in template_filepaths] + searchpaths
        template_filepath = self._find_file(template_filepaths, searchpaths)
        if not template_filepath:
            msg = f"None of the templates {_humanify(template_filepaths)} found at {_humanify(searchpaths)}."
            raise MakolatorError(msg)
        lookup = self._create_template_lookup([template_filepath.parent] + searchpaths)
        return Template(filename=str(template_filepath), lookup=lookup)

    def _create_template_lookup(self, searchpaths: List[Path]) -> TemplateLookup:
        cache_path = self.cache_path

        def get_module_filename(filepath, uri):
            # pylint: disable=unused-argument
            hash_ = hashlib.sha256()
            hash_.update(bytes(str(filepath), encoding="utf-8"))
            ident = hash_.hexdigest()
            return cache_path / f"{filepath.name}_{ident}.py"

        return TemplateLookup(
            directories=[str(item) for item in searchpaths],
            cache_dir=self.cache_path,
            input_encoding="utf-8",
            output_encoding="utf-8",
            modulename_callable=get_module_filename,
        )

    @staticmethod
    def _find_file(filepaths: List[Path], searchpaths: List[Path]) -> Optional[Path]:
        """Find `filepath` in `searchpaths` and return first match."""
        for filepath in filepaths:
            if filepath.is_absolute():
                # absolute
                if filepath.exists():
                    return filepath
            else:
                # relative
                for searchpath in searchpaths:
                    joined = searchpath / filepath
                    if joined.exists():
                        return joined
        return None

    def _get_context_dict(self, output_filepath, context: Optional[dict] = None):
        result = {
            "datamodel": self.datamodel,
            "output_filepath": output_filepath,
            "render": self.render,
            # "render_inline": render_inline,
        }
        if context:
            result.update(context)
        return result

    @contextmanager
    def _handle_render_exceptions(self, template_paths: List[Path]):
        try:
            yield
        except TemplateLookupException as exc:
            raise RuntimeError(f"{exc!s} in paths {_humanify(template_paths)}") from exc


def _humanify(iterable):
    if iterable:
        return ", ".join(repr(str(item)) for item in iterable)
    return "''"
