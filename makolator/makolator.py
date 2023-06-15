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
from typing import List

from attrs import define
from mako.lookup import TemplateLookup
from mako.template import Template
from outputfile import open_

from .config import Config
from .datamodel import Datamodel

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

    __cache_path: Path = None

    def __del__(self):
        if self.__cache_path:
            rmtree(self.__cache_path)

    @property
    def _cache_path(self) -> Path:
        if self.config.cache_path:
            return self.config.cache_path

        if not self.__cache_path:
            self.__cache_path = Path(tempfile.mkdtemp(prefix="makolator"))
        return self.__cache_path

    @contextmanager
    def open_outputfile(self, filepath: Path, encoding: str = "utf-8"):
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
        with open_(filepath, encoding=encoding, mkdir=True) as file:
            try:
                yield file
            finally:
                file.close()
                if self.config.verbose:
                    print(f"'{filepath!s}'... {file.state.value}")

    def render_str(self, template: str, dest: Path = None, context: dict = None):
        """
        Render Template String.

        TODO: Example

        Args:
            template: Multi-Line Template String

        Keyword Args:
            dest: Destination File. STDOUT by default.
            context: Key-value pairs in dictionary propagated to the template.
        """
        lookup = self._get_template_lookup(self.config.template_paths)
        Template(template, lookup=lookup)
        # TODO

    def render(self, templates: List[Path], dest: Path = None, context: dict = None):
        """
        Render First Found Template To ``dest`` file.

        TODO: Example

        Args:
            templates: Template Filenames.

        Keyword Args:
            dest: Destination File. STDOUT by default.
            context: Key-value pairs in dictionary propagated to the template.

        """
        # TODO

    def render_inplace_str(self, template: str, dest: Path, context: dict = None):
        """
        Render Inplace Marker from Template String.

        TODO: Example

        Args:
            template: Multi-Line Template String

        Keyword Args:
            dest: Destination File. STDOUT by default.
            context: Key-value pairs in dictionary propagated to the template.
        """
        lookup = self._get_template_lookup(self.config.template_paths)
        Template(template, lookup=lookup)

    def render_inplace(self, templates: List[Path], dest: Path, context: dict = None):
        """
        Render Inplace Marker in ``dest`` file.

        TODO: Example

        Args:
            templates: Template Filenames.

        Keyword Args:
            dest: Destination File. STDOUT by default.
            context: Key-value pairs in dictionary propagated to the template.
        """
        # TODO

    def _get_template_lookup(self, directories) -> TemplateLookup:
        cache_path = self._cache_path

        def get_module_filename(filepath, uri):
            # pylint: disable=unused-argument
            hash_ = hashlib.sha256()
            hash_.update(bytes(filepath, encoding="utf-8"))
            ident = hash_.hexdigest()
            return cache_path / f"{filepath.name}_{ident}.py"

        return TemplateLookup(
            directories=directories,
            input_encoding="utf-8",
            output_encoding="utf-8",
            modulename_callable=get_module_filename,
        )
