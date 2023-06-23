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
Extended Mako Templates for Python.

Makolator is not makulation. It extends the https://www.makotemplates.org/ engine by the following features:

* Simple API
* Keep timestamp of generated files, if content did not change (a gift for every build system user)
* Easy hierarchical template usage
* Inplace File Rendering

This is how to use it
---------------------

Initialize
~~~~~~~~~~

Just create your instance of :any:`Makulator`

>>> from makolator import Makolator
>>> mklt = Makolator()

Configure
~~~~~~~~~

The config attribute contains all settings.
See :any:`Config` for a complete documentation.
The most relevant settings are search paths for general templates ...

>>> mklt.config.template_paths
[]

... and the replacement strategy for :any:`outputfile.Existing` files:

>>> mklt.config.existing
<Existing.KEEP_TIMESTAMP: 'keep_timestamp'>

If you want to place templates in the actual working directory - set it as search path:

>>> from pathlib import Path
>>> mklt.config.template_paths = [Path('.')]

If you like it verbose - try:

>>> mklt.config.verbose = True

Rendering
~~~~~~~~~

Assume you have this template in a file
(please ignore the `...` here - they are just there for a proper python example):

>>> Path('file.txt.mako').write_text('''\\
... <%def name="top(name)">\\
... generated-top: ${name}
... </%def>\\
... <%def name="bot(name, **kwargs)">\\
... generated-bot: ${name} ${kwargs}
... </%def>\\
... ${datamodel}
... ${top('foo')}\\
... ${bot('foo', b=4)}\\
... ''') and None

:any:`gen` use ``sys.stdout`` by default ...

>>> mklt.gen([Path('file.txt.mako')])
Datamodel()
generated-top: foo
generated-bot: foo {'b': 4}

... or use ``dest`` for file creation - the verbose mode shares some nice information:

>>> mklt.gen([Path('file.txt.mako')], dest=Path("file.txt"))
'file.txt'... CREATED.
>>> mklt.gen([Path('file.txt.mako')], dest=Path("file.txt"))
'file.txt'... identical. untouched.

Datamodel
~~~~~~~~~

The :any:`Datamodel` is your container to forward data to the template.

>>> mklt.datamodel.mydata = {'a': 0, 'b': 1}

The output looks like that:

>>> mklt.gen([Path('file.txt.mako')])
Datamodel(mydata={'a': 0, 'b': 1})
generated-top: foo
generated-bot: foo {'b': 4}

and you get notified about the changed content:

>>> mklt.gen([Path('file.txt.mako')], dest=Path("file.txt"))
'file.txt'... UPDATED.

Differential output
~~~~~~~~~~~~~~~~~~~

If you like it even more verbose - try:

>>> mklt.config.diffout = print

This will send any diff of the updated files to stdout.

>>> mklt.datamodel.mydata['b'] = 2
>>> mklt.gen([Path('file.txt.mako')], dest=Path("file.txt")) # doctest: +SKIP
---
+++
@@ -1,3 +1,3 @@
-Datamodel(mydata={'a': 0, 'b': 1})
+Datamodel(mydata={'a': 0, 'b': 2})
 generated-top: foo
 generated-bot: foo {'b': 4}
<BLANKLINE>
'file.txt'... UPDATED.

By default this is disabled:

>>> mklt.config.diffout = None

Inplace Rendering
~~~~~~~~~~~~~~~~~

One key feature is the inplace rendering.

Assume you have a handwritten file and you just want to update/generate a part of it.
`GENERATE INPLACE` will become your new friend:

>>> Path('inplace.txt').write_text('''\\
... I am a regular text file.
... This is handwritten text.
... GENERATE INPLACE BEGIN top('bar')
...   this line will be replaced
... GENERATE INPLACE END top
... This is handwritten text too.
... ''') and None

>>> mklt.inplace([Path('file.txt.mako')], Path("inplace.txt"))
'inplace.txt'... UPDATED.

>>> print(Path('inplace.txt').read_text())
I am a regular text file.
This is handwritten text.
GENERATE INPLACE BEGIN top('bar')
generated-top: bar
GENERATE INPLACE END top
This is handwritten text too.
<BLANKLINE>


That's it.
"""

# pylint: disable=unused-import
from outputfile import Existing

from .config import Config
from .datamodel import Datamodel
from .escape import tex
from .exceptions import MakolatorError
from .makolator import Makolator
