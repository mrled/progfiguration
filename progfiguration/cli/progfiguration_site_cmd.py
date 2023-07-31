"""The command line interface for progfiguration"""

import argparse
import datetime
import importlib
import importlib.metadata
import json
import logging
import os
import pathlib
import subprocess
import sys
import tempfile
import time
from typing import List, Optional

import progfiguration
from progfiguration import logger, progfigbuild, remotebrute, sitewrapper
from progfiguration.cli.util import (
    CommaSeparatedStrList,
    configure_logging,
    get_command_help,
    idb_excepthook,
    progfiguration_error_handler,
    progfiguration_log_levels,
    syslog_excepthook,
)
from progfiguration.inventory import Inventory
from progfiguration.progfigsite_validator import validate


def _action_version_core():
    """Retrieve the version of progfiguration core"""

    coreversion = importlib.metadata.version("progfiguration")
    result = [
        f"progfiguration core:",
        f"    path: {pathlib.Path(progfiguration.__file__).parent}",
        f"    version: {coreversion}",
    ]
    print("\n".join(result))


def _action_version_all(inventory: Inventory):
    """Retrieve the version of progfiguration core and the progfigsite"""

    progfigsite = sitewrapper.get_progfigsite()

    try:
        builddata_version = sitewrapper.site_submodule("builddata.version")
        version = builddata_version.version
        builddate = builddata_version.builddate
    except ModuleNotFoundError:
        version = progfigsite.get_version()
        builddate = datetime.datetime.utcnow()

    result = [
        f"progfigsite:",
        f"    path: {sitewrapper.get_progfigsite_path()}",
        f"    name: {progfigsite.site_name}",
        f"    description: {progfigsite.site_description}",
        f"    build date: {version}",
        f"    version: {builddate}",
    ]

    _action_version_core()
    print("\n".join(result))


def _action_apply(inventory: Inventory, nodename: str, roles: Optional[List[str]] = None, force: bool = False):
    """Apply configuration for the node 'nodename' to localhost"""

    if roles is None:
        roles = []

    node = inventory.node(nodename).node

    if node.TESTING_DO_NOT_APPLY and not force:
        raise Exception(
            f"Was going to apply progfiguration to node {nodename} but TESTING_DO_NOT_APPLY is True for that node."
        )

    for role in inventory.node_role_list(nodename):
        if not roles or role.name in roles:
            try:
                logging.debug(f"Running role {role.name}...")
                role.apply()
                logging.info(f"Finished running role {role.name}.")
            except Exception as exc:
                logging.error(f"Error running role {role.name}: {exc}")
                raise
        else:
            logging.info(f"Skipping role {role.name}.")

    logging.info(f"Finished running all roles")


def _action_list(inventory: Inventory, collection: str):
    if collection == "nodes":
        for node in inventory.nodes:
            print(node)
    elif collection == "groups":
        for group in inventory.groups:
            print(group)
    elif collection == "functions":
        for function in inventory.functions:
            print(function)
    else:
        raise Exception(f"Unknown collection {collection}")


def _action_info(inventory: Inventory, nodes: List[str], groups: List[str], functions: List[str]):
    if not any([nodes, groups, functions]):
        print("Request info on a node, group, or function. (See also the 'list' subcommand.)")
    for nodename in nodes:
        node_groups = inventory.node_groups[nodename]
        node_group_commas = ", ".join(node_groups)
        node_function = inventory.node_function[nodename]
        node_roles = inventory.function_roles[node_function]
        node_roles_commas = ", ".join(node_roles)
        print(f"Node {nodename} (function {node_function}):")
        print(f"  Groups: {node_group_commas}")
        print(f"  Roles: {node_roles_commas}")
    for groupname in groups:
        group_members = inventory.group_members[groupname]
        group_members_commas = ", ".join(group_members)
        print(f"Group {groupname}:")
        print(f"  Members: {group_members_commas}")
    for funcname in functions:
        function_nodes = ", ".join(inventory.function_nodes[funcname])
        function_roles = ", ".join(inventory.function_roles[funcname])
        print(f"Function {funcname}:")
        print(f"  Nodes: {function_nodes}")
        print(f"  Roles: {function_roles}")


def _action_encrypt(
    inventory: Inventory,
    name: str,
    value: str,
    nodes: List[str],
    groups: List[str],
    controller_key: bool,
    store: bool,
    stdout: bool,
):
    encrypted_value, recipients = inventory.encrypt_secret(name, value, nodes, groups, controller_key, store=store)
    print("Encrypted for all of these recipients:")
    for pk in recipients:
        print(pk)
    if stdout:
        print(encrypted_value)


def _action_decrypt(inventory: Inventory, nodes: List[str], groups: List[str], controller_key: bool):
    age_path = inventory.age_path
    if not age_path:
        raise Exception("Could not find age key")
    for node in nodes:
        print(f"Secrets for node {node}:")
        print("---")
        decrypted_secrets = {k: v.decrypt(age_path) for k, v in inventory.get_node_secrets(node).items()}
        print(json.dumps(decrypted_secrets, indent=2, sort_keys=True))
        print("---")
    for group in groups:
        print(f"Secrets for group {group}:")
        print("---")
        decrypted_secrets = {k: v.decrypt(age_path) for k, v in inventory.get_group_secrets(group).items()}
        print(json.dumps(decrypted_secrets, indent=2, sort_keys=True))
        print("---")
    if controller_key:
        print(f"Secrets for the controller:")
        print("---")
        decrypted_secrets = {k: v.decrypt(age_path) for k, v in inventory.get_controller_secrets().items()}
        print(json.dumps(decrypted_secrets, indent=2, sort_keys=True))
        print("---")


def _action_deploy_apply(
    inventory: Inventory,
    nodenames: List[str],
    groupnames: List[str],
    roles: List[str],
    remote_debug: bool,
    force_apply: bool,
    keep_remote_file: bool,
):

    if roles is None:
        roles = []

    for group in groupnames:
        nodenames += inventory.group_members[group]
    nodenames = list(set(nodenames))

    nodes = {n: inventory.node(n).node for n in nodenames}

    errors: list[dict[str, str]] = []

    with tempfile.TemporaryDirectory() as tmpdir:
        pyzfile = pathlib.Path(os.path.join(tmpdir, "progfiguration.pyz"))
        progfigbuild.build_progfigsite_zipapp(sitewrapper.get_progfigsite_path(), pyzfile)
        for nname, node in nodes.items():
            args = []
            if remote_debug:
                args.append("--debug")
            args += ["apply", nname]
            if force_apply:
                args.append("--force-apply")
            if roles:
                args += ["--roles", ",".join(roles)]

            # To run progfiguration remotely over ssh, we need:
            # * To run Python unbuffered with -u
            # * To ask sshd to create a tty with -tt
            # * To redirect stdin to /dev/null,
            #   which fixes some weird issues with bad newlines in the output for reasons I don't understand.
            # The result isn't perfect, as some lines are not printed exactly as they were in the output, but it's ok.
            try:
                remotebrute.cpexec(
                    f"{node.user}@{node.address}",
                    pyzfile.as_posix(),
                    args,
                    interpreter=["python3", "-u"],
                    ssh_tty=True,
                    ssh_stdin=subprocess.DEVNULL,
                    keep_remote_file=keep_remote_file,
                )
            # except subprocess.CalledProcessError as exc:
            except Exception as exc:
                print(f"Error running progfiguration on node {nname}:")
                logger.debug(exc)
                errors.append({"node": nname, "error": str(exc)})

    if errors:
        print("====================")
        print("Errors running progfiguration on {len(errors)} node(s):")
        for error in errors:
            print(f"  {error['node']}: {error['error']}")


def _action_deploy_copy(
    inventory: Inventory,
    nodenames: List[str],
    groupnames: List[str],
    remotepath: str,
):
    for group in groupnames:
        nodenames += inventory.group_members[group]
    nodenames = list(set(nodenames))

    nodes = {n: inventory.node(n).node for n in nodenames}

    with tempfile.TemporaryDirectory() as tmpdir:
        pyzfile = pathlib.Path(os.path.join(tmpdir, "progfiguration.pyz"))
        progfigbuild.build_progfigsite_zipapp(sitewrapper.get_progfigsite_path(), pyzfile)
        for nname, node in nodes.items():
            remotebrute.scp(f"{node.user}@{node.address}", pyzfile.as_posix(), remotepath)


def _action_validate():
    validation = validate(progfiguration.progfigsite_module_path)
    if validation.is_valid:
        print(f"Progfigsite (Python path: '{progfiguration.progfigsite_module_path}') is valid.")
    else:
        print(
            f"Progfigsite (Python path: '{progfiguration.progfigsite_module_path}') has {len(validation.errors)} errors:"
        )
    for attrib in validation.errors:
        print(attrib.errstr)


def _make_parser():
    parser = argparse.ArgumentParser("progfiguration site management tool")

    group_onerr = parser.add_mutually_exclusive_group()
    group_onerr.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Open the debugger if an unhandled exception is encountered",
    )
    group_onerr.add_argument(
        "--syslog-exception",
        action="store_true",
        help="When encountering an unhandle exception, print exception details to syslog before exiting",
    )

    parser.add_argument(
        "--log-stderr",
        default="NOTSET",
        choices=progfiguration_log_levels,
        help="Log level to send to stderr. Defaults to NOTSET (all messages, including debug). NONE to disable.",
    )

    def syslog_default():
        if os.path.exists("/dev/log"):
            return "INFO"
        return "NONE"

    parser.add_argument(
        "--log-syslog",
        default=syslog_default(),
        choices=progfiguration_log_levels,
        help="Log level to send to syslog. Defaults to INFO if /dev/log exists, otherwise NONE. NONE to disable. If a value other than NONE is passed explicitly and /dev/log does not exist, an exception will be raised.",
    )

    parser.add_argument(
        "--age-private-key", "-k", help="The path to an age private key that decrypts inventory secrets"
    )

    # node/group related options
    node_opts = argparse.ArgumentParser(add_help=False)
    node_opts.add_argument(
        "--nodes", "-n", default=[], type=CommaSeparatedStrList, help="A node, or list of nodes separated by commas"
    )
    node_opts.add_argument(
        "--groups", "-g", default=[], type=CommaSeparatedStrList, help="A group, or list of groups separated by commas"
    )

    # function related options
    func_opts = argparse.ArgumentParser(add_help=False)
    func_opts.add_argument(
        "--functions",
        "-f",
        default=[],
        type=CommaSeparatedStrList,
        help="A function, or list of functions separated by commas",
    )

    # --controller option
    # TODO: document that everything is always encrypted for the controller
    ctrl_opts = argparse.ArgumentParser(add_help=False)
    ctrl_opts.add_argument(
        "--controller", "-c", action="store_true", help="En/decrypt to/from the controller secret store"
    )

    # --roles option
    roles_opts = argparse.ArgumentParser(add_help=False)
    roles_opts.add_argument(
        "--roles",
        "-r",
        default=[],
        type=CommaSeparatedStrList,
        help="A role, or list of roles separated by commas. The role(s) must be defined in the inventory for the node(s).",
    )

    subparsers = parser.add_subparsers(dest="action", required=True)

    # version subcommand
    svn_all = subparsers.add_parser("version", description="Show progfiguration core and progfigsite versions")

    # apply subcommand
    sub_apply = subparsers.add_parser("apply", parents=[roles_opts], description="Apply configuration")
    sub_apply.add_argument("nodename", help="The name of a node in the progfiguration inventory")
    sub_apply.add_argument(
        "--force-apply", action="store_true", help="Force apply, even if the node has TESTING_DO_NOT_APPLY set."
    )

    # deploy subcommand
    sub_deploy = subparsers.add_parser(
        "deploy",
        parents=[node_opts],
        description="Deploy progfiguration to remote system in inventory as a pyz package; requires passwordless SSH configured",
    )
    sub_deploy_subparsers = sub_deploy.add_subparsers(dest="deploy_action", required=True)
    sub_deploy_sub_apply = sub_deploy_subparsers.add_parser(
        "apply", parents=[roles_opts], description="Deploy and apply configuration"
    )
    sub_deploy_sub_apply.add_argument(
        "--remote-debug",
        action="store_true",
        help="Open the debugger on the remote system if an unhandled exception is encountered",
    )
    sub_deploy_sub_apply.add_argument(
        "--force-apply", action="store_true", help="Force apply, even if the node has TESTING_DO_NOT_APPLY set."
    )
    sub_deploy_sub_apply.add_argument(
        "--keep-remote-file", action="store_true", help="Don't delete the remote file after execution"
    )
    sub_deploy_sub_copy = sub_deploy_subparsers.add_parser(
        "copy", description="Copy the configuration to the remote system"
    )
    default_dest = f"/tmp/progfiguration-{str(time.time()).replace('.', '')}.pyz"
    sub_deploy_sub_copy.add_argument(
        "--destination",
        "-d",
        default=default_dest,
        help=f"The destination path on the remote system, default is based on the time this program was started, like {default_dest}",
    )

    # list subcommand
    sub_list = subparsers.add_parser("list", description="List inventory items")
    list_choices = ["nodes", "groups", "functions", "svcpreps"]
    sub_list.add_argument(
        "collection",
        choices=list_choices,
        help=f"The items to list. Options: {list_choices}",
    )

    # info subcommand
    sub_info = subparsers.add_parser(
        "info", parents=[node_opts, func_opts], description="Display info about nodes and groups"
    )

    # encrypt subcommand
    sub_encrypt = subparsers.add_parser(
        "encrypt", parents=[node_opts, ctrl_opts], description="Encrypt a value with age"
    )
    sub_encrypt_value_group = sub_encrypt.add_mutually_exclusive_group()
    sub_encrypt_value_group.add_argument("--value", help="Encrypt this value")
    sub_encrypt_value_group.add_argument("--file", help="Encrypt the contents of this file")
    sub_encrypt.add_argument(
        "--save-as",
        help="Save under this name in each node/group's secret store. Otherwise, just print to stdout and do not save.",
    )
    sub_encrypt.add_argument("--stdout", action="store_true", help="Print encrypted value to stdout")

    # decrypt subcommand
    sub_decrypt = subparsers.add_parser(
        "decrypt", parents=[node_opts, ctrl_opts], description="Decrypt secrets from the secret store"
    )

    # validate subcommand
    sub_validate = subparsers.add_parser(
        "validate", description="Validate the progfigsite that it matches the required API"
    )

    # debugger subcommand
    # This is useful for debugging a pyz deployment,
    # since you can't just 'import progfiguration' inside a python3 interpreter
    # because the pyz is not on the PYTHONPATH.
    sub_debugger = subparsers.add_parser(
        "debugger",
        description="Open a debugger on localhost.",
    )

    # Return
    return parser


def _main_implementation(*arguments):
    parser = _make_parser()
    parsed = parser.parse_args(arguments[1:])

    if parsed.debug:
        sys.excepthook = idb_excepthook
    elif parsed.syslog_exception:
        sys.excepthook = syslog_excepthook
    configure_logging(parsed.log_stderr, parsed.log_syslog)

    # Later actions do require an inventory

    # Get a nodename, if we have one
    try:
        nodename = parsed.nodename
    except AttributeError:
        nodename = None

    inventory = Inventory(
        sitewrapper.site_submodule_resource("", "inventory.conf"),
        progfiguration.progfigsite_module_path,
        age_privkey=parsed.age_private_key,
        current_node=nodename,
    )

    validation = validate(progfiguration.progfigsite_module_path)
    if not validation.is_valid:
        print(
            f"Progfigsite (Python path: '{progfiguration.progfigsite_module_path}') has {len(validation.errors)} errors:"
        )
        for attrib in validation.errors:
            print(attrib.errstr)

    if parsed.action == "version":
        _action_version_all(inventory)
    elif parsed.action == "apply":
        _action_apply(inventory, parsed.nodename, roles=parsed.roles, force=parsed.force_apply)
    elif parsed.action == "deploy":
        if not parsed.nodes and not parsed.groups:
            parser.error("You must pass at least one of --nodes or --groups")
        if parsed.deploy_action == "apply":
            _action_deploy_apply(
                inventory,
                parsed.nodes,
                parsed.groups,
                roles=parsed.roles,
                remote_debug=parsed.remote_debug,
                force_apply=parsed.force_apply,
                keep_remote_file=parsed.keep_remote_file,
            )
        elif parsed.deploy_action == "copy":
            _action_deploy_copy(inventory, parsed.nodes, parsed.groups, parsed.destination)
            print(f"Copied to remote host(s) at {parsed.destination}")
        else:
            parser.error(f"Unknown deploy action {parsed.deploy_action}")
    elif parsed.action == "list":
        _action_list(inventory, parsed.collection)
    elif parsed.action == "info":
        _action_info(inventory, parsed.nodes, parsed.groups, parsed.functions)
    elif parsed.action == "encrypt":
        if not parsed.nodes and not parsed.groups and not parsed.controller:
            parser.error("You must pass at least one of --nodes, --groups, or --controller")
        if not parsed.value and not parsed.file:
            parser.error("You must pass one of --value or --file")
        if parsed.file:
            with open(parsed.file) as fp:
                value = fp.read()
        else:
            value = parsed.value
        _action_encrypt(
            inventory,
            parsed.save_as or "",
            value,
            parsed.nodes,
            parsed.groups,
            parsed.controller,
            bool(parsed.save_as),
            parsed.stdout,
        )
    elif parsed.action == "decrypt":
        if not parsed.nodes and not parsed.groups and not parsed.controller:
            parser.error("You must pass at least one of --nodes, --groups, or --controller")
        _action_decrypt(inventory, parsed.nodes, parsed.groups, parsed.controller)
    elif parsed.action == "validate":
        # We always validate but this shows a nice message even if validation succeeds
        _action_validate()
    else:
        parser.error(f"Unknown action {parsed.action}")


def main(progfigsite_modpath: str):
    """The main function for the progfigsite command-line interface

    While this file exists in the core progfiguration package,
    it is not installed as a command-line script there.
    Instead, progfigsite packages are expected to add a shim file that calls this function,
    and configure their Python project to install that shim file as a command-line script.

    This function expects an argument that is the Python module path to the progfigsite package.
    For instance, if the progfigsite package is installed as 'my_progfigsite',
    then this argument should be 'my_progfigsite'.
    This package is expected to be installed in the same Python environment as the progfiguration package.
    Building a pip package with `progfiguration build pip`
    will use that shim file to call this function.
    Building a pyz package with `progfiguration build pyz`
    will install the site package as `progfigsite` in the pyz regardless of what the site package is called,
    and will call this function with `progfigsite` as the argument.

    TODO: document how the modpath thing works
    """
    progfiguration.progfigsite_module_path = progfigsite_modpath

    # mypy flags this for no reason and I can't figure out why, YOLO
    # > Argument 2 to "progfiguration_error_handler" has incompatible type "*list[str]"; expected "list[str]"  [arg-type]mypy(error)
    progfiguration_error_handler(_main_implementation, *sys.argv)  # type: ignore


__doc__ = f"""
The command-line interface for a progfigsite.

This command is installed with a progfigsite package.
When packaging a progfigsite in a pyz,
running the pyz will run this command.

This command can interact with site nodes,
encrypt and decrypt secrets (if an appropriate private key is available),
and apply a node's roles to the local machine.

## Command line help

The program's command-line help is reproduced here:

```text
{get_command_help("progfigsite", _make_parser())}
```
"""
