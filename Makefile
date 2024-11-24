# based on https://ricardoanderegg.com/posts/makefile-python-project-tricks/

# Override PWD so that it's always based on the location of the file and **NOT**
# based on where the shell is when calling `make`. This is useful if `make`
# is called like `make -C <some path>`
PWD := $(realpath $(dir $(abspath $(firstword $(MAKEFILE_LIST)))))
MAKEFILE_PWD := $(CURDIR)

# Using $$() instead of $(shell) to run evaluation only when it's accessed
# https://unix.stackexchange.com/a/687206
PYTHON = $$(if [ -d $(PWD)/'.venv' ]; then echo $(PWD)/".venv/bin/python3"; else echo "python3"; fi)

# https://earthly.dev/blog/python-makefile/#phony-targets
# [...] tell "make" not to consider an existing file with the same name.
.PHONY: help clean test install

help:
	echo "options: ["hello", "clean", "test", "install"]"

hello:
	echo "Hello, World"

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

test:
	$(PYTHON) scripts/run_tests.py

install:
	$(PYTHON) setup.py --verbose build
