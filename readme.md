# progfiguration

PROGrammatic conFIGURATION.
I'm tired of writing YAML when what I want to write is Python.

## Building and publishing

```sh
# Create a venv
python3 -m venv venv
# Enter the venv
. venv/bin/activate
# Make sure pip is recent - required for our pyproject.toml-only package
python3 -m pip install --upgrade pip
# Install this directory as editable, and include development dependencies
python3 -m pip install --editable '.[development]'
# Run unit tests
python3 -m unittest
# Build a source-only distribution of the package
python3 -m build -s
# Upload it to PyPI
twine upload dist/*
```

We only actually need to build a source version of the package,
because progfiguration expects that your progfigsite package will pull in the source code.
We avoid building the binary version because it takes longer.

## Testing

After entering the venv (see above), run unit tests with `python3 -m unittest`.
You can modify the test run with a few environment variables:

* `PROGFIGURATION_TEST_DEBUG=1`: Launch a debugger on any test failure or exception
* `PROGFIGURATION_TEST_SLOW_ALL=1`: Run all slow tests
* `PROGFIGURATION_TEST_SLOW_PACKAGING=1`: Run slow tests related to packaging (`progfiguration build`, etc)
