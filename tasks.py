"""progfiguration development tasks"""


import invoke


@invoke.task
def tests(ctx, debug=False, slow=False):
    """Run normal tests, but not slower packaging tests"""
    env = {}
    if debug:
        env["PROGFIGURATION_TEST_DEBUG"] = "1"
    if slow:
        env["PROGFIGURATION_TEST_SLOW_ALL"] = "1"
    ctx.run("python3 -m unittest -v", env=env)


@invoke.task
def docsclean(ctx):
    """Clean the documentation build directory"""
    ctx.run("rm -rf docs/_build")


@invoke.task
def docsdev(ctx):
    """Run a local development server for the documentation, and rebuild on changes"""
    ctx.run("sphinx-autobuild docs/src docs/_build/html")


@invoke.task
def docsbuild(ctx):
    """Build the documentation and exit"""
    ctx.run("sphinx-build docs/src docs/_build/html")


@invoke.task
def make_release(ctx):
    """Make a release"""

    try:
        import tomllib
    except ImportError:
        raise RuntimeError("tomllib (from Python 3.11+) is required to make a release")

    """
    #Shell script version:

    version="$(python -c 'import tomllib; f=open("./pyproject.toml", "rb"); proj=tomllib.load(f); print(proj["project"]["version"])')"

    git commit pyproject.toml docs/src/appendix/changelog.rst -m "Release version $version"

    git tag "v${version}" master
    git push origin "v${version}"
    git push

    # Build a source-only distribution of the package
    python3 -m build -s
    # Upload it to PyPI
    twine upload "dist/progfiguration-${version}.tar.gz"
    """

    version = tomllib.load(open("./pyproject.toml", "rb"))["project"]["version"]
    ctx.run(f"git commit pyproject.toml docs/src/appendix/changelog.rst -m 'Release version {version}'")
    ctx.run(f"git tag 'v{version}' master")
    ctx.run(f"git push origin 'v{version}'")
    ctx.run("git push")

    # Build a source-only distribution of the package
    ctx.run("python3 -m build -s")
    # Upload it to PyPI
    ctx.run(f"twine upload 'dist/progfiguration-{version}.tar.gz'")
