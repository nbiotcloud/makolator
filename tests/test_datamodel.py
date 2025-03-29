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
"""Datamodel Testing."""

from makolator import Datamodel


def test_datamodel():
    """Basic Testing on Datamodel."""
    datamodel = Datamodel()
    assert datamodel.__dict__ == {}
    assert str(datamodel) == "Datamodel()"
    assert repr(datamodel) == "Datamodel()"


def test_datamodel_init():
    """Initialize Data Model."""
    datamodel = Datamodel(a="bc", d=4)
    assert datamodel.__dict__ == {"a": "bc", "d": 4}
    text = "Datamodel(a='bc', d=4)"
    assert str(datamodel) == text
    assert repr(datamodel) == text


def test_datamodel_update():
    """Update Datamodel Later."""
    datamodel = Datamodel(a="bc")
    assert datamodel.__dict__ == {"a": "bc"}
    datamodel.data = 4
    text = "Datamodel(a='bc', data=4)"
    assert datamodel.__dict__ == {"a": "bc", "data": 4}
    assert str(datamodel) == text
    assert repr(datamodel) == text
