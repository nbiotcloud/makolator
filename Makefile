_GREEN:=\033[0;32m
_BLUE:=\033[0;34m
_BOLD:=\033[1m
_NORM:=\033[0m
ENV:=uv run --frozen --


.PHONY: help
help:  ## [DEFAULT] Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?##"}; {printf "${_BLUE}${_BOLD}%-10s${_NORM} %s\n", $$1, $$2}'


.PHONY: all
all:  ## Do everything taggged with [ALL] below
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep "\[ALL\]" | grep -v "^all" | awk 'BEGIN {FS = ":.*?##"}; {printf "%s ", $$1}' | xargs make
	@echo "\n    ${_GREEN}${_BOLD}PASS${_NORM}\n"


.PHONY: pre-commit
pre-commit: .venv/.valid .git/hooks/pre-commit ## [ALL] Run 'pre-commit' on all files
	${ENV} pre-commit run --all-files

.git/hooks/pre-commit: .venv/.valid
	${ENV} pre-commit install --install-hooks


.PHONY: test
test: .venv/.valid ## [ALL] Run Unittests via 'pytest' with {PYTEST_OPTIONS}
	${ENV} pytest -vv ${PYTEST_OPTIONS}
	@echo  "See coverage report:\n\n    file://${PWD}/htmlcov/index.html\n"


.PHONY: checktypes
checktypes: .venv/.valid ## [ALL] Run Type-Checking via 'mypy'
	${ENV} mypy .


.PHONY: doc
doc: doc-static .venv/.valid ## [ALL] Build Documentation via 'mkdocs'
	${ENV} mkdocs build # --strict


.PHONY: doc-static
doc-static:  .venv/.valid ## Static Documentation Content
	mkdir -p docs/static
	${ENV} makolator --help > docs/static/cli.txt
	${ENV} makolator gen --help > docs/static/cli.gen.txt
	${ENV} makolator inplace --help > docs/static/cli.inplace.txt
	${ENV} makolator clean --help > docs/static/cli.clean.txt
	cd docs/static && cp inplace-pre.txt inplace.txt && ${ENV} makolator inplace inplace.txt.mako inplace.txt
	cd docs/static && cp inplace-mako-pre.txt inplace-mako.txt && ${ENV} makolator inplace inplace-mako.txt
	cd docs/static && ${ENV} makolator gen test.txt.mako test.txt
	cd docs/static && cp static-pre.txt static.txt && ${ENV} makolator gen static.txt.mako static.txt


.PHONY: doc-serve
doc-serve: doc-static .venv/.valid ## Start Local Documentation Server via 'mkdocs'
	${ENV} mkdocs serve --no-strict


.PHONY: code
code:  ## Start Visual Studio Code
	code makolator.code-workspace &


.PHONY: clean
clean:  ## Remove everything mentioned by '.gitignore' file
	git clean -xdf


.PHONY: distclean
distclean:  ## Remove everything mentioned by '.gitignore' file and UNTRACKED files
	git clean -xdf


.PHONY: shell
shell:  ## Open a project specific SHELL. For leaving use 'exit'.
	${ENV} ${SHELL}


# Helper
.venv/.valid: pyproject.toml uv.lock
	uv sync --frozen
	@touch $@

uv.lock:
	uv lock
