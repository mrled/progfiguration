"""The command line interface for progfiguration"""

import argparse
import importlib
import importlib.metadata
import pathlib
import sys
import textwrap

import progfiguration
from progfiguration import progfigbuild, sitewrapper
from progfiguration.cli.util import (
    configure_logging,
    idb_excepthook,
    progfiguration_error_handler,
    progfiguration_log_levels,
)
from progfiguration.newsite import make_progfigsite
from progfiguration.progfigsite_validator import validate


def _action_version_core(quiet: bool = False):
    """Retrieve the version of progfiguration core"""

    coreversion = importlib.metadata.version("progfiguration")
    if quiet:
        print(coreversion)
    else:
        result = [
            f"progfiguration core:",
            f"    path: {pathlib.Path(progfiguration.__file__).parent}",
            f"    version: {coreversion}",
        ]
        print("\n".join(result))


def _action_validate(module_path: str):
    """Validate a progfigsite module

    Arguments:
        module_path -- The Python path to the progfigsite module
    """
    validation = validate(module_path)
    if validation.is_valid:
        print(f"Progfigsite (Python path: '{module_path}') is valid.")
    else:
        print(f"Progfigsite (Python path: '{module_path}') has {len(validation.errors)} errors:")
    for attrib in validation.errors:
        print(attrib.errstr)


def _make_parser():
    parser = argparse.ArgumentParser("progfiguration core management tool")

    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Open the debugger if an unhandled exception is encountered",
    )

    parser.add_argument(
        "--log-stderr",
        default="NOTSET",
        choices=progfiguration_log_levels,
        help="Log level to send to stderr. Defaults to NOTSET (all messages, including debug). NONE to disable.",
    )

    # options for finding the progfigsite
    site_opts = argparse.ArgumentParser(add_help=False)
    site_opts.add_argument(
        "--progfigsite-fspath",
        type=pathlib.Path,
        help="The filesystem path to a progfigsite package, like /path/to/progfigsite. You must also pass --progfigsite-modname with this argument, because we do not read pyproject.toml or any other file to find the module name automatically.",
    )
    site_opts.add_argument(
        "--progfigsite-modname",
        type=str,
        help="The module name for a progfigsite package, like 'my_progfigsite'. If --progfigsite-fspath is specified, use this name for the module found at that path on the filesystem. If --progfigsite-fspath is not specified, expect to find a progfigsite module with this name in the Python path already.",
    )

    subparsers = parser.add_subparsers(dest="action", required=True)

    # version-core subcommand
    svn = subparsers.add_parser("version", description="Show progfiguration core version")
    svn.add_argument("--quiet", "-q", action="store_true", help="Only print the version string")

    # build subcommand
    sub_build = subparsers.add_parser("build", parents=[site_opts], description="Build the package")
    sub_build_subparsers = sub_build.add_subparsers(dest="buildaction", required=True)
    sub_build_sub_pyz = sub_build_subparsers.add_parser(
        "pyz",
        description="Build a zipapp .pyz file containing the Python module. Must be run from an editable install.",
    )
    sub_build_sub_pyz.add_argument("pyzfile", type=pathlib.Path, help="Save the resulting pyz file to this path")
    sub_build_sub_pip = sub_build_subparsers.add_parser(
        "pip",
        description="Build a pip package containing the Python module. Must be run from an editable install.",
    )
    sub_build_sub_pip.add_argument(
        "--outdir",
        default="./dist",
        type=pathlib.Path,
        help="Save the resulting pip package to this path. Defaults to ./dist",
    )
    sub_build_sub_pip.add_argument(
        "--keep-injected-files",
        action="store_true",
        default=False,
        help="Keep the injected files in the package after building. This is useful for debugging.",
    )

    # validate subcommand
    sub_validate = subparsers.add_parser(
        "validate", parents=[site_opts], description="Validate the progfigsite that it matches the required API"
    )

    # newsite subcommand
    sub_newsite = subparsers.add_parser("newsite", description="Create a new progfigsite package")
    sub_newsite.add_argument(
        "--name",
        default="progfigsite",
        help="The name of the progfigsite package to create. Defaults to '%(default)s'.",
    )
    sub_newsite.add_argument(
        "--path",
        type=pathlib.Path,
        help="The path to create the progfigsite package in. Defaults to a directory named after the --name argument in the current directory.",
    )
    sub_newsite.add_argument(
        "--description",
        default="A progfigsite package",
        help="The description of the progfigsite package to create. Defaults to '%(default)s'.",
    )
    # TODO: how will users create sites with alternative secret backends?
    sub_newsite.add_argument(
        "--controller-age-key-path",
        type=pathlib.Path,
        help="The path to the controller age key. Defaults to 'SITENAME.controller.age' in the current directory. Make sure this is stored securely!",
    )

    # Return
    return parser


def _main_implementation(*arguments):
    parser = _make_parser()
    parsed = parser.parse_args(arguments[1:])

    if parsed.debug:
        sys.excepthook = idb_excepthook
    configure_logging(parsed.log_stderr)

    # Subcommands that don't need an existing progfigsite

    if parsed.action == "version":
        _action_version_core(quiet=parsed.quiet)
        return

    elif parsed.action == "newsite":
        path = parsed.path or pathlib.Path(parsed.name)
        controllerage = parsed.controller_age_key_path or pathlib.Path(f"{parsed.name}.controller.age")
        controllerage = controllerage.resolve()
        make_progfigsite(parsed.name, path, parsed.description, controllerage)
        rootpkg = path / parsed.name
        print(
            textwrap.dedent(
                f"""\
                Created new progfigsite package '{parsed.name}' at '{path}'. Next steps:

                    * Run `progfiguration validate --progfigsite-fspath {rootpkg} --progfigsite-modname {parsed.name}` to validate the package.
                    * Edit '{rootpkg}/inventory.conf' to include your hosts, roles, groups, and functions.
                    * Create node and group files in '{rootpkg}/nodes' and '{rootpkg}/groups'.
                    * Write your roles in '{rootpkg}/roles'.
                """
            )
        )
        return

    # Subcommands that need an existing progfigsite

    if parsed.progfigsite_fspath and parsed.progfigsite_modname:
        sitewrapper.set_progfigsite_by_filepath(parsed.progfigsite_fspath, parsed.progfigsite_modname)
    elif parsed.progfigsite_modname:
        sitewrapper.set_progfigsite_by_module_name(parsed.progfigsite_modname)
    else:
        parser.error(
            f"For action {parsed.action}, must specify --progfigsite-modname if the site is already in the Python path, or both --progfigsite-fspath and --progfigsite-modname to find the site on the filesystem outside of the Python path."
        )
    progfigsite_modpath = parsed.progfigsite_modname
    progfigsite_fspath = sitewrapper.get_progfigsite_path()

    if parsed.action == "build":
        if parsed.buildaction == "pyz":
            progfigbuild.build_progfigsite_zipapp(progfigsite_fspath, parsed.progfigsite_modname, parsed.pyzfile)
        elif parsed.buildaction == "pip":
            progfigbuild.build_progfigsite_pip(
                progfigsite_fspath,
                parsed.progfigsite_modname,
                parsed.outdir,
                keep_injected_files=parsed.keep_injected_files,
            )
        else:
            parser.error(f"Unknown buildaction {parsed.buildaction}")
        return
    elif parsed.action == "validate":
        _action_validate(progfigsite_modpath)
        return

    parser.error(f"Unknown action {parsed.action}")


def main():
    """The main entry point for the progfiguration command-line interface"""
    progfiguration_error_handler(_main_implementation, *sys.argv)
