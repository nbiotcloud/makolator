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
   * - ``gen``
     - :any:`Makolator.gen` - generate file
   * - ``inplace``
     - :any:`Makolator.inplace` - update file

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

The lines between ``GENERATE INLINE BEGIN`` and ``GENERATE INLINE END`` can be
filled via a template like:

.. literalinclude:: static/inplace.txt.mako
   :language: text

An inplace update (``makolator inplace file.txt``) will result in:

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


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
