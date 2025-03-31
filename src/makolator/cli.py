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
Command Line Interface.
"""

import argparse
from pathlib import Path

from makolator import Config, Existing, Info, Makolator, get_cli


def main(args=None):
    """Command Line Interface Processing."""
    parser = argparse.ArgumentParser(
        prog="makolator",
        description="Mako Templates (https://www.makotemplates.org/) extended.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="cmd")
    default_config = Config()

    gen = subparsers.add_parser(
        "gen",
        help="Generate File",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""\
Generate a file from a template:

    makolator gen test.txt.mako test.txt

Generate a file from a template and fallback to 'default.txt.mako' if 'test.txt.mako' is missing:

    makolator gen test.txt.mako default.txt.mako test.txt
""",
    )
    gen.add_argument("templates", nargs="+", type=Path, help="Template Files. At least one must exist")
    gen.add_argument("output", type=Path, help="Output File")

    inplace = subparsers.add_parser(
        "inplace",
        help="Update File Inplace",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""\
Update with inplace template only:

    makolator inplace test.txt

Update a file from a template:

    makolator inplace test.txt.mako test.txt

Update a file from a template and fallback to 'default.txt.mako' if 'test.txt.mako' is missing:

    makolator inplace test.txt.mako default.txt.mako test.txt
""",
    )
    inplace.add_argument("templates", nargs="*", type=Path, help="Optional Template Files")
    inplace.add_argument("inplace", type=Path, help="Updated File")
    inplace.add_argument(
        "--ignore-unknown",
        "-i",
        action="store_true",
        help="Ignore unknown template function calls.",
    )

    clean = subparsers.add_parser(
        "clean",
        help="Remove Fully-Generated Files",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""\
Remove all files with '@fully-generated' in header.
The number of inspected lines at the top of a file is defined by --tag_lines.

    makolator clean .

""",
    )
    clean.add_argument("paths", nargs="+", type=Path, help="Paths to look for files.")

    for sub in (gen, inplace, clean):
        sub.add_argument("--verbose", "-v", action="store_true", help="Tell what happens to the file.")
        sub.add_argument("--show-diff", "-s", action="store_true", help="Show what lines changed.")
        sub.add_argument(
            "--tag_lines",
            default=default_config.tag_lines,
            help=f"Number of Inspected Lines on 'clean'. Default is {default_config.tag_lines}.",
        )
        sub.add_argument("--stat", "-S", action="store_true", help="Print Statistics")
    for sub in (gen, inplace):
        sub.add_argument(
            "--existing",
            "-e",
            default="keep_timestamp",
            choices=[item.value for item in Existing],
            help="What if the file exists. Default is 'keep_timestamp'",
        )
        sub.add_argument(
            "--template-path",
            "-T",
            type=Path,
            default=[],
            action="append",
            help="Directories with templates referred by include/inherit/...",
        )
        sub.add_argument(
            "--marker-fill",
            type=str,
            help=(
                "Static Code, Inplace and Template Marker are filled with "
                "this given value until reaching line length of --marker-linelength."
            ),
        )
        sub.add_argument(
            "--marker-linelength",
            type=int,
            help=("Static Code, Inplace and Template Marker are filled until --marker-linelength."),
        )
        sub.add_argument("--eol", "-E", help="EOL comment on generated lines")

    args = parser.parse_args(args=args)
    if args.cmd:
        if args.cmd == "clean":
            config = Config(
                verbose=args.verbose,
                diffout=print if args.show_diff else None,
                tag_lines=args.tag_lines,
                track=args.stat,
            )
        else:
            config = Config(
                verbose=args.verbose,
                diffout=print if args.show_diff else None,
                existing=args.existing,
                template_paths=[*args.template_path, Path()],
                marker_fill=args.marker_fill,
                marker_linelength=args.marker_linelength,
                inplace_eol_comment=args.eol,
                tag_lines=args.tag_lines,
                track=args.stat,
            )
        info = Info(cli=get_cli())
        mklt = Makolator(config=config, info=info)
        if args.cmd == "gen":
            mklt.gen(args.templates, args.output)
        elif args.cmd == "inplace":
            mklt.inplace(args.templates, args.inplace, ignore_unknown=args.ignore_unknown)
        elif args.cmd == "clean":
            mklt.clean(args.paths)
        if config.track:
            print(mklt.tracker.stat)
    else:
        parser.print_help()
