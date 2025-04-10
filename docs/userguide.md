# User Guide

## Template Writing

[https://www.makotemplates.org/](https://www.makotemplates.org/) documents the template language.
Within the template the following symbols are available

| Symbol | Description |
|---|---|
| `datamodel` | [`Datamodel`][makolator.Datamodel] - the data container |
| `output_filepath` | [`pathlib.Path`][pathlib.Path] with outputfile path |
| `output_tags` | `tuple[str, ...]` with tags about code-generation type, see [Tags](#tags) |
| `makolator` | [`Makolator`][makolator.Makolator] - Makolator Engine |
| `makolator.open_outputfile` | [`Makolator.open_outputfile`][makolator.Makolator.open_outputfile] - Create file handle with timestamp preserving. |
| `makolator.gen` | [`Makolator.gen`][makolator.Makolator.gen] - generate file |
| `makolator.inplace` | [`Makolator.inplace`][makolator.Makolator.inplace] - update file |
| `makolator.clean` | [`Makolator.clean`][makolator.Makolator.clean] - remove fully-generated files |
| `makolator.info` | [`Makolator.info`][makolator.Makolator.info] - Information Container |
| `run` | `run` - Identical to [`subprocess.run`][subprocess.run] and capture `stdout`. |
| `indent` | Indent single line or multiple lines by two spaces: `${text | indent}` |
| `indent(spaces)` | Indent single line or multiple lines by given number of spaces: `${text | indent(4)}` |
| `indent(spaces, rstrip=True)` | Indent single line or multiple lines by given number of spaces, but avoid end-line whitespaces: `${text | indent(4, rstrip=True)}` |
| `prefix(text)` | Prefix single line or multiple lines by given text: `${text | prefix('// ')}` |
| `prefix(text, rstrip=True)` | Prefix single line or multiple lines by given text, but avoid end-line whitespaces: `${text | prefix('// ', rstrip=True)}` |
| `comment(text)` | Prefix single line or multiple lines by comment separator from ``Config``: `${text | comment('Text set as comment')}` |
| `tex` | Escape latex special characters: `${text | tex}` |


### Tags

| Tag | Description |
|---|---|
| `@generated` | Always included, as all files are generated |
| `@fully-generated` | Included if the file is generated via [`Makolator.gen`][makolator.Makolator.gen] and does not include any static-code which must be kept. |
| `@inplace-generated` | Included if the file is created via [`Makolator.inplace`][makolator.Makolator.inplace] |

### `run` Examples

```
run(['echo', '"Hello World"'])
run('echo "Hello World"', shell=True)
run('mycmd --output file && cat file', shell=True)
```
The variable `${TMPDIR}` in the arguments will be replaced by a temporary directory path.

## File Generation

The template ``test.txt.mako``:

```text
--8<-- "docs/static/test.txt.mako"
```

A generate (``makolator gen test.txt.mako test.txt``) will result in:

```text
--8<-- "docs/static/test.txt"
```


## Inplace Code Generation

Assume the following file:

```text
--8<-- "docs/static/inplace-pre.txt"
```

The lines between ``GENERATE INPLACE BEGIN`` and ``GENERATE INPLACE END`` can be
filled via a template like:

```text
--8<-- "docs/static/inplace.txt.mako"
```

An inplace update (``makolator inplace inplace.txt.mako file.txt``) will result in:

  ```text
  --8<-- "docs/static/inplace.txt"
  ```


## Inplace Skeleton

The inplce code generation is a powerful mechanism.
There is only the challenge to create a proper file with
placeholders at the beginning.
A template is allowed to serve a `<%def name="create_inplace()">`:

```text
--8<-- "docs/static/inplace-create.txt.mako"
```

A missing inplace file is an error by default.
The `-c` option activates the `create_inplace` mechanism:
``makolator inplace inplace-create.txt.mako file-create.txt -c``

```text
--8<-- "docs/static/file-create.txt"
```


## Inplace Template

The file can contain templates too:

```text
--8<-- "docs/static/inplace-mako-pre.txt"
```

The inplace update (``makolator inplace file.txt``) will result in:

```text
--8<-- "docs/static/inplace-mako.txt"
```


## Static Code

Fully and inplace generated files might want to leave space
for user manipulation, which is kept even on update.
These locations need to be prepared by ``${staticcode('name')}``, where
``name`` is a unique identifier within the target file.

Assume the following template:

```text
--8<-- "docs/static/static.txt.mako"
```

and an outdated generated file:

```text
--8<-- "docs/static/static-pre.txt"
```

An update (``makolator gen file.txt.mako file.txt``) will result in:

```text
--8<-- "docs/static/static.txt"
```
