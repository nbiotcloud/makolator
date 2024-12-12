Extended Mako Templates for Python
==================================

Links
-----

- `PyPI - Python Package Index <https://pypi.org/project/makolator/>`_
- `Source Code <https://github.com/nbiotcloud/makolator>`_
- `Issues <https://github.com/nbiotcloud/makolator/issues>`_

Programming Interface
---------------------

.. toctree::
   :maxdepth: 1

   api/makolator

Command Line
------------

`makolator` has two sub-commands `gen` and `inplace`:

.. literalinclude:: static/cli.txt
   :language: text

Generate
~~~~~~~~

.. literalinclude:: static/cli.gen.txt
   :language: text

Inplace
~~~~~~~

.. literalinclude:: static/cli.inplace.txt
   :language: text

Template Writing
----------------

https://www.makotemplates.org/ documents the template language.
Within the template the following symbols are available

.. list-table:: Template Symbols
   :widths: 25 75
   :header-rows: 1

   * - Symbol
     - Description
   * - ``datamodel``
     - :any:`Datamodel` - the data container
   * - ``output_filepath``
     - ``pathlib.Path`` with outputfile path
   * - ``makolator``
     - :any:`Makolator` - Makolator Engine
   * - ``makolator.open_outputfile``
     - :any:`Makolator.open_outputfile` - Create file handle with timestamp preserving.
   * - ``makolator.gen``
     - :any:`Makolator.gen` - generate file
   * - ``makolator.inplace``
     - :any:`Makolator.inplace` - update file
   * - ``makolator.info``
     - :any:`Makolator.info` - Information Container
   * - ``run``
     - :any:`run` - Identical to :any:`subprocess.run` and capture ``stdout``.

       Examples:

         * ``run(['echo', '"Hello World"'])``
         * ``run('echo "Hello World"', shell=True)``
         * ``run('mycmd --output file && cat file', shell=True)``

       The variable ``${TMPDIR}`` in the arguments will be replaced by a temporary directory
       path.
   * - ``indent``
     - Indent single line or multiple lines by two spaces:

       ``${text | indent}``
   * - ``indent(spaces)``
     - Indent single line or multiple lines by given number of spaces:

       ``${text | indent(4)}``
   * - ``prefix(text)``
     - Prefix single line or multiple lines by given text:

       ``${text | prefix('// ')}``
   * - ``comment(text)``
     - Prefix single line or multiple lines by comment separator from ``Config``:

       ``${text | comment('Text set as comment')}``
   * - ``tex``
     - Escape latex special characters:

       ``${text | tex}``

File Generation
~~~~~~~~~~~~~~~

The template ``test.txt.mako``:

.. literalinclude:: static/test.txt.mako
   :language: text

A generate (``makolator gen test.txt.mako test.txt``) will result in:

.. literalinclude:: static/test.txt
   :language: text



Inplace Code Generation
~~~~~~~~~~~~~~~~~~~~~~~

Assume the following file:

.. literalinclude:: static/inplace-pre.txt
   :language: text

The lines between ``GENERATE INPLACE BEGIN`` and ``GENERATE INPLACE END`` can be
filled via a template like:

.. literalinclude:: static/inplace.txt.mako
   :language: text

An inplace update (``makolator inplace test.txt.mako file.txt``) will result in:

.. literalinclude:: static/inplace.txt
   :language: text


Inplace Template
~~~~~~~~~~~~~~~~

The file can contain templates too:

.. literalinclude:: static/inplace-mako-pre.txt
   :language: text

The inplace update (``makolator inplace file.txt``) will result in:

.. literalinclude:: static/inplace-mako.txt
   :language: text

Static Code
~~~~~~~~~~~

Fully and inplace generated files might want to leave space
for user manipulation, which is kept even on update.
These locations need to be prepared by ``${staticcode('name')}``, where
``name`` is a unique identifier within the target file.

Assume the following template:

.. literalinclude:: static/static.txt.mako
   :language: text

and an outdated generated file:

.. literalinclude:: static/static-pre.txt
   :language: text

An update (``makolator gen file.txt.mako file.txt``) will result in:

.. literalinclude:: static/static.txt
   :language: text

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
