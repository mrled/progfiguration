"""Command-line scripts (and helpers)"""

import argparse
import importlib
import json
import logging
import logging.handlers
import os
import pathlib
import pdb
import sys
import traceback
from collections.abc import Callable
from io import StringIO
from typing import Dict, List

from progfiguration import logger
from progfiguration.util import import_module_from_filepath


"""Log levels that our command-line programs can configure"""
progfiguration_log_levels = [
    # Levels from the library
    "CRITICAL",
    "ERROR",
    "WARNING",
    "INFO",
    "DEBUG",
    "NOTSET",
    # My customization
    "NONE",
]


class ProgfigurationTerminalError(Exception):
    """A terminal error that can be used to print a nice message"""

    def __init__(self, message, returncode):
        super().__init__(message)
        self.returncode = returncode


def progfiguration_error_handler(func: Callable[[List[str]], int], *arguments: List[str]) -> int:
    """Special error handler

    Wrap the main() function in this to properly handle the following cases:

    * Broken pipes.
      The EPIPE signal is sent if you run e.g. `script.py | head`.
      Wrapping the main function with this one exits cleanly if that happens.
      See <https://docs.python.org/3/library/signal.html#note-on-sigpipe>
    * Errors with ProgfigurationTerminalError
      These errors are intended to display nice messages to the user.
    """
    try:
        returncode = func(*arguments)
        sys.stdout.flush()
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        # Convention is 128 + whatever the return code would otherwise be
        returncode = 128 + 1
        sys.exit(returncode)
    except ProgfigurationTerminalError as pte:
        print(pte.message)
        sys.exit(pte.returncode)

    return returncode


def idb_excepthook(type, value, tb):
    """Call an interactive debugger in post-mortem mode

    If you do "sys.excepthook = idb_excepthook", then an interactive debugger
    will be spawned at an unhandled exception
    """
    if hasattr(sys, "ps1") or not sys.stderr.isatty():
        sys.__excepthook__(type, value, tb)
    else:
        traceback.print_exception(type, value, tb)
        print
        pdb.pm()


def syslog_excepthook(type, value, tb):
    """Send an unhandled exception to syslog"""
    # Note that format_exception() returns
    # "a list of strings, each ending in a newline and some containing internal newlines"
    # <https://docs.python.org/3/library/traceback.html#traceback.format_exception>
    exc = "".join(traceback.format_exception(type, value, tb))
    logger.error(f"Encountered unhandled exception and must exit :(")
    for line in exc.splitlines():
        logger.error(line)


def configure_logging(log_stderr: str, log_syslog: str = "NONE") -> None:
    if log_stderr != "NONE":
        handler_stderr = logging.StreamHandler()
        handler_stderr.setFormatter(logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"))
        handler_stderr.setLevel(log_stderr)
        logger.addHandler(handler_stderr)
    if log_syslog != "NONE":
        if not os.path.exists("/dev/log"):
            raise FileNotFoundError("There is no /dev/log on this system, cannot configure syslog logger")
        handler_syslog = logging.handlers.SysLogHandler(address="/dev/log")
        handler_syslog.setLevel(log_syslog)
        logger.addHandler(handler_syslog)


def get_progfigsite_module_opts() -> argparse.ArgumentParser:
    # options for finding the progfigsite
    site_opts = argparse.ArgumentParser(add_help=False)
    site_grp = site_opts.add_mutually_exclusive_group(required=True)
    site_grp.add_argument(
        "--progfigsite-filesystem-path",
        type=pathlib.Path,
        help="The filesystem path to a progfigsite package, like /path/to/progfigsite. If neither this nor --progfigsite-python-path is passed, look for a 'progfigsite' package in the Python path.",
    )
    site_grp.add_argument(
        "--progfigsite-python-path",
        type=str,
        help="The python path to a progfigsite package, like 'my_progfigsite' or 'one.two.three.progfigsite'. If neither this nor --progfigsite-filesystem-path is passed, look for a 'progfigsite' package in the Python path.",
    )
    return site_opts


def find_progfigsite_module(parser: argparse.ArgumentParser, parsed: argparse.Namespace):
    """Find the progfigsite module from the command line arguments"""

    if parsed.progfigsite_filesystem_path:
        progfigsite_filesystem_path = parsed.progfigsite_filesystem_path
        progfigsite, progfigsite_module_path = import_module_from_filepath(parsed.progfigsite_filesystem_path)
    elif parsed.progfigsite_python_path:
        progfigsite_module_path = parsed.progfigsite_python_path
        progfigsite = importlib.import_module(progfigsite_module_path)
        progfigsite_filesystem_path = pathlib.Path(progfigsite.__file__).parent
    else:
        parser.error(f"Missing progfigsite path option")

    return (progfigsite, progfigsite_module_path, progfigsite_filesystem_path)
