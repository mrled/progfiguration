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
