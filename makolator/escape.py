"""Escape reserved characters."""

import re
from typing import Optional

__TEX_CONV = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\^{}",
    "\\": r"\textbackslash{}",
    "<": r"\textless{}",
    ">": r"\textgreater{}",
    "®": r"\textsuperscript{\textregistered}",
    "©": r"\textcopyright{}",
    "™": r"\textsuperscript{\texttrademark}",
}
__TEX_REGEX = re.compile("|".join(re.escape(key) for key in sorted(__TEX_CONV.keys(), key=lambda item: -len(item))))


def tex(text: Optional[str]):
    r"""
    Escape (La)Tex.

    >>> tex("Foo & Bar")
    'Foo \\& Bar'
    >>> tex(None)

    Args:
        text: tex
    Returns:
        escaped string.
    """
    if text is None:
        return None
    return __TEX_REGEX.sub(lambda match: __TEX_CONV[match.group()], str(text))
