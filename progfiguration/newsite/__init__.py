"""Support for creating a new progfigsite."""


import importlib.resources
import pathlib
from typing import Optional
from progfiguration.age import AgeKey
from progfiguration.cmd import magicrun

from progfiguration.temple import Temple


def write_file_from_template(template_name, target_path: pathlib.Path, template_args: Optional[dict]):
    """Write a file from a template

    Arguments:
        template_path -- The name of a template file in this package
        target_path -- The path to the target file
        template_args -- The arguments to pass to the template
    """

    if template_args is None:
        template_args = {}

    temple_str = importlib.resources.read_text(__package__, template_name)
    temple = Temple(temple_str)
    rendered = temple.substitute(**template_args)
    target_path.write_text(rendered)


def make_package_dir(
    path: pathlib.Path,
    init_contents: Optional[str] = None,
    init_temple_name: Optional[str] = None,
    init_temple_args: Optional[dict] = None,
):
    """Make a Python package (or subpackage) directory and set up the __init__.py file.

    The init file can be either a string or a template for write_file_from_template.

    Return the input path.
    """

    if init_contents is None and init_temple_name is None:
        raise RuntimeError("Must provide either init_contents or init_temple_name")
    elif init_contents is not None and init_temple_name is not None:
        raise RuntimeError("Must provide either init_contents or init_temple_name, not both")

    path.mkdir()

    if init_contents:
        with (path / "__init__.py").open("w") as f:
            f.write(init_contents)
    else:
        write_file_from_template(init_temple_name, path / "__init__.py", init_temple_args)

    return path


def make_progfigsite(name: str, path: pathlib.Path, description: str, controller_age_path: pathlib.Path):
    """Create a new progfigsite package

    Arguments:
        name -- The name of the progfigsite package to create
        path -- The path to create the progfigsite package in
    """

    if path.exists():
        raise RuntimeError(f"Path {path} already exists")
    if controller_age_path.exists():
        raise RuntimeError(f"Controller age key path {controller_age_path} already exists")

    controller_age = AgeKey.generate(path=controller_age_path)

    pyprojdir = path

    pyprojdir.mkdir(parents=True)
    write_file_from_template(
        "pyproject.toml.temple",
        pyprojdir / "pyproject.toml",
        {"name": name, "description": description},
    )
    write_file_from_template("readme.md.temple", pyprojdir / "readme.md", {"name": name})

    rootpkg = make_package_dir(
        pyprojdir / name,
        init_temple_name="progfigsite-init.py.temple",
        init_temple_args={"name": name, "description": description},
    )
    write_file_from_template(
        "inventory.conf.temple",
        rootpkg / "inventory.conf",
        {
            "controller_age_path": controller_age_path.as_posix(),
            "controller_age_pub": controller_age.public,
        },
    )

    clidir = make_package_dir(rootpkg / "cli", init_contents='"""Command line utilities for the progfigsite."""\n')
    write_file_from_template("progfigsite_shim.py.temple", clidir / "progfigsite_shim.py", {})

    make_package_dir(
        rootpkg / "autovendor",
        init_contents='"""Automatically vendored packages.\n\nDo not copy modules into this directory yourself.\nProgfiguration will copy dependencies here during build time.\n"""\n',
    )
    make_package_dir(
        rootpkg / "builddata",
        init_contents='"""The builddata module\n\nNo files should be added to this directory in source control.\nIt is reserved for injections of data at build time only.\n"""\n',
    )
    make_package_dir(
        rootpkg / "sitelib",
        init_contents='"""Site library. Any site specific data, helper functions, etc belongs here."""\n',
    )

    groups_dir = make_package_dir(rootpkg / "groups", init_contents='"""Groups."""\n')
    write_file_from_template("exgroup.py", groups_dir / "group1.py", {})
    write_file_from_template("universalgrp.py", groups_dir / "universal.py", {})

    nodes_dir = make_package_dir(rootpkg / "nodes", init_contents='"""Nodes."""\n')
    write_file_from_template("exnode.py", nodes_dir / "node1.py", {})

    roles_dir = make_package_dir(rootpkg / "roles", init_contents='"""Roles."""\n')
    write_file_from_template("exrole.py", roles_dir / "role1.py", {})
