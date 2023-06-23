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
Command Line Interface.
"""
import argparse
from pathlib import Path

from makolator import Config, Existing, Makolator


def main(args=None):
    """Command Line Interface Processing."""
    parser = argparse.ArgumentParser(
        prog="makolator",
        description="Mako Templates (https://www.makotemplates.org/) extended.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="cmd")

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

    for sub in (gen, inplace):
        sub.add_argument("--verbose", "-v", action="store_true", help="Tell what happens to the file.")
        sub.add_argument("--show-diff", "-s", action="store_true", help="Show what lines changed.")
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

    args = parser.parse_args(args=args)
    if args.cmd:
        config = Config(
            verbose=args.verbose,
            diffout=print if args.show_diff else None,
            existing=args.existing,
            template_paths=args.template_path + [Path(".")],
        )
        mklt = Makolator(config=config)
        if args.cmd == "gen":
            mklt.gen(args.templates, args.output)
        else:
            mklt.inplace(args.templates, args.inplace, ignore_unknown=args.ignore_unknown)
    else:
        parser.print_help()
