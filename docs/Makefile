# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = build
APIOPTS       = --separate --force --module-first --maxdepth 2 --no-toc

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: api gen Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Quick HTML rebuild which skips generating the static files:
quick-html: api Makefile
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

api:
	sphinx-apidoc --output-dir api .. ../makolator/cli ../docs ../tests $(wildcard ../*.py) $(APIOPTS)
.PHONY: api

gen:
	mkdir -p static
	makolator --help > static/cli.txt
	makolator gen --help > static/cli.gen.txt
	makolator inplace --help > static/cli.inplace.txt
	cd static && cp inplace-pre.txt inplace.txt && makolator inplace inplace.txt.mako inplace.txt
	cd static && cp inplace-mako-pre.txt inplace-mako.txt && makolator inplace inplace-mako.txt
	cd static && makolator gen test.txt.mako test.txt
