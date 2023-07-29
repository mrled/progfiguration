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
# Run progfiguration itself
progfiguration --help
```

We only actually need to build a source version of the package,
because progfiguration expects that your progfigsite package will pull in the source code.
We avoid building the binary version because it takes longer.

### Building the documentation

```sh
# Build the docs once, without running a webserver
sphinx-build -b html docs/ docs/_build/html
# Build the docs whenever a change is detected, and run a webserver that supports automatic live reload
sphinx-autobuild docs docs/_build/html &
```

## Testing

After entering the venv (see above), run unit tests with `python3 -m unittest`.
You can modify the test run with a few environment variables:

* `PROGFIGURATION_TEST_DEBUG=1`: Launch a debugger on any test failure or exception
* `PROGFIGURATION_TEST_SLOW_ALL=1`: Run all slow tests
* `PROGFIGURATION_TEST_SLOW_PACKAGING=1`: Run slow tests related to packaging (`progfiguration build`, etc)

## Building the example sites

In the same venv as above:

```sh
# Install the example progfigsite
python3 -m pip install --editable 'tests/data/simple[development]'
# Run the progfigsite itself
progfigsite --help
```

## Making a release

1.  Check out the `master` branch.
    Make sure your checkout is clean, with all changes committed to git and pushed to Github
2.  Set the version in `pyproject.toml`.
    Don't commit the change yet.
    We'll read this file to determine the version to tag in git and push to PyPI.
    *   This will require Python 3.11 because we parse the TOML file directly with `tomllib`.
    *   We can't use `progfiguration version` for this because it will return the version as it was at install time.
3.  Run the following:

```sh
version="$(python -c 'import tomllib; f=open("./pyproject.toml", "rb"); proj=tomllib.load(f); print(proj["project"]["version"])')"

git commit pyproject.toml -m "Release version $version"

git tag "v${version}" master
git push origin "v${version}"

# Build a source-only distribution of the package
python3 -m build -s
# Upload it to PyPI
twine upload "dist/progfiguration-${version}.tar.gz"
```

The documentation will be updated with the lastest version number and content as well via Github Actions.
