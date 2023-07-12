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
# Build the packagej
python3 -m build
# Upload it to PyPI
twine upload dist/*
```
