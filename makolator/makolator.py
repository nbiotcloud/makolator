"""
The Makolator.

A simple API to an improved Mako.
"""

import hashlib
import logging
import re
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from shutil import rmtree
from typing import List, Optional

from attrs import define
from mako.exceptions import TemplateLookupException, text_error_template
from mako.lookup import TemplateLookup
from mako.runtime import Context
from mako.template import Template
from outputfile import Existing, open_

from .config import Config
from .datamodel import Datamodel
from .exceptions import MakolatorError
from .util import _InplaceInfo

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

    def render_file(self, template_filepaths: List[Path], dest: Optional[Path] = None, context: Optional[dict] = None):
        """
        Render template file.

        Args:
            template_filepaths: Templates.

        Keyword Args:
            dest: Output File.
            context: Key-Value Pairs pairs forwarded to the template.
        """
        LOGGER.debug("render_file(%r, %r)", [str(filepath) for filepath in template_filepaths], dest)
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

    def render_file_inplace(
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
        LOGGER.debug("render_file_inlplace(%r, %r)", [str(filepath) for filepath in template_filepaths], filepath)
        template_paths = self.config.template_paths
        with self._handle_render_exceptions(template_paths):
            template = self._create_template_from_filepaths(template_filepaths, template_paths)
        with self._handle_render_exceptions([Path(item) for item in template.lookup.directories]):
            self._render_inplace(template, filepath, ignore_unknown, context)

    def _render_inplace(self, template: Template, filepath: Path, ignore_unknown: bool, context: Optional[dict] = None):
        # pylint: disable=too-many-locals
        LOGGER.debug("_render_inplace(%r, %r)", template.filename, filepath)
        marker = self.config.inplace_marker
        start = re.compile(rf"(?P<indent>\s*).*{marker}\s+BEGIN\s(?P<funcname>[a-z_]+)\((?P<args>.*)\).*")
        end = None
        func = None
        with self.open_outputfile(filepath, existing=Existing.KEEP_TIMESTAMP, newline="") as outputfile:
            with open(filepath, encoding="utf-8") as inputfile:
                for lineno, line in enumerate(inputfile.readlines(), 1):
                    if end is None:
                        # populate
                        outputfile.write(line)
                        # search for "BEGIN <funcname>(<args>)"
                        startmatch = start.match(line)
                        if startmatch:
                            # consume BEGIN
                            info = _InplaceInfo(filepath, lineno, **startmatch.groupdict())
                            try:
                                func = template.get_def(info.funcname)
                            except AttributeError as exc:
                                if not ignore_unknown:
                                    raise MakolatorError(
                                        f"{filepath!s}:{info.lineno} Function '{info.funcname}' "
                                        f"is not found in template '{template.filename}'."
                                    ) from exc
                            else:
                                end = re.compile(rf"(?P<indent>\s*).*{marker}\s+END\s{info.funcname}.*")
                    else:
                        # search for "END <funcname>"
                        endmatch = end.match(line)
                        if endmatch:
                            # fill
                            self._fill_inplace(outputfile, info, func, context)
                            # propagate END tag
                            outputfile.write(line)
                            self._check_indent(filepath, lineno, info, endmatch)
                            # consume END
                            end = None
                if end is not None:
                    raise MakolatorError(
                        f"{filepath!s}:{info.lineno} BEGIN tag " f"{info.funcname}({info.args})' without END tag."
                    )

    @staticmethod
    def _check_indent(filepath: Path, lineno: int, info: _InplaceInfo, endmatch: re.Match):
        if endmatch.group("indent") != info.indent:
            LOGGER.warning(
                "%s:%d Indent of END tag %s does not match indent of BEGIN tag %s.",
                filepath,
                lineno,
                len(info.indent),
                len(endmatch.group("indent")),
            )

    def _fill_inplace(self, output, info: _InplaceInfo, func, context: Optional[dict]):
        # determine args, kwargs
        inplacecontext = self._get_context_dict(info.filepath, context=context)
        funccontext = {"_extract": _extract}
        funccontext.update(inplacecontext)
        try:
            # pylint: disable=eval-used
            args, kwargs = eval(f"_extract({info.args})", funccontext)
        except SyntaxError as exc:
            raise MakolatorError(
                f"{info.filepath!s}:{info.lineno} Function invocation failed. "
                f"{exc.__class__.__name__} in arguments: '{info.funcname}({info.args})'."
            ) from exc
        except Exception as exc:
            raise MakolatorError(
                f"{info.filepath!s}:{info.lineno} Function invocation failed. "
                f"{exc!r} in arguments: '{info.funcname}({info.args})'."
            ) from exc

        inplacecontext.update(**kwargs)
        # run func(args, kwargs)
        try:
            # _render_inplace() uses the universal newline. Mako already took care about newlines,
            # what is not useful here. We ignore it by using splitlines and dumping out line by line
            # by ourselfs.
            lines = func.render_unicode(*args, **inplacecontext).splitlines()
            indent = info.indent
            for line in lines:
                if line:
                    output.write(f"{indent}{line}\n")
                else:
                    output.write("\n")
        except Exception as exc:
            debug = str(text_error_template().render())
            raise MakolatorError(
                f"{info.filepath!s}:{info.lineno} Function '{info.funcname}' " f"invocation failed. {exc!r}. {debug}"
            ) from exc

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
            "render_file": self.render_file,
            "render_file_inplace": self.render_file_inplace,
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


def _extract(*args, **kwargs):
    return (args, kwargs)
