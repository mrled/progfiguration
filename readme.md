# progfiguration

PROGrammatic conFIGURATION.
I'm tired of writing YAML when what I want to write is Python.

## Development

Make and activate a venv, and install as editable.

```sh
python3 -m venv venv
. venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install --editable '.[development]'
```

From there:

* `progfiguration --help` to run the program
* `invoke -l` to list tasks for building documentation, running tests, and making releases

### Building and releasing

We only actually need to build a source version of the package,
because progfiguration expects that your progfigsite package will pull in the source code.
We avoid building the binary version because it takes longer.

### Testing

Run tests with `invoke tests`.
Run with `--slow` to run slow tests too.
Special environment variables:

* `PROGFIGURATION_TEST_VERBOSE=1`: Show verbose output, including stdout/stderr of commands run inside of tests
* `PROGFIGURATION_TEST_DEBUG=1`: Launch a debugger on any test failure or exception
* `PROGFIGURATION_TEST_SLOW_ALL=1`: Run all slow tests (same as `invoke tests --slow`)
* `PROGFIGURATION_TEST_SLOW_PACKAGING=1`: Run just slow tests related to packaging (`progfiguration build`, etc)

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
2.  Set the version in `pyproject.toml` and update `docs/appendix/changelog.rst`.
    Don't commit the change yet.
    We'll read this file to determine the version to tag in git and push to PyPI.
    *   This will require Python 3.11 because we parse the TOML file directly with `tomllib`.
    *   We can't use `progfiguration version` for this because it will return the version as it was at install time.
3.  Run `invoke make-release`

The documentation will be updated with the lastest version number and content as well via Github Actions.
