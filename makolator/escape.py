"""Escape reserved characters."""

import re

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


def tex(text):
    r"""
    Escape (La)Tex.

    >>> tex("Foo & Bar")
    'Foo \\& Bar'
    >>> tex(None)

    Args:
        text (str): tex
    Returns:
        (str): escaped string.
    """
    if text is None:
        return None
    return __TEX_REGEX.sub(lambda match: __TEX_CONV[match.group()], str(text))
