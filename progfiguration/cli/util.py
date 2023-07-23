"""Utilities for command-line programs"""

import argparse
from collections.abc import Callable
import logging
import logging.handlers
import os
import pdb
import sys
import textwrap
import traceback
from typing import List

from progfiguration import logger

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
"""Log levels that our command-line programs can configure
Taken from the logging module,
see <https://docs.python.org/3/library/logging.html#logging-levels>.
Includes NONE, which is a special value that means "don't configure logging at all".
"""


def progfiguration_error_handler(func: Callable[[List[str]], int], *arguments: List[str]) -> int:
    """Special error handler
    Wrap a `main()` function in this to properly handle broken pipes.
    The `EPIPE` signal is sent if you run e.g. `script.py | head`.
    Wrapping the main function with this one exits cleanly if that happens.
    See <https://docs.python.org/3/library/signal.html#note-on-sigpipe>.
    Params:
    * `func`: The main function to wrap, which should take a list of arguments and return an exit code.
    * `arguments`: A list of arguments to pass to `func`, probably from `sys.argv[1:]`.
    Returns:
    * The exit code from `func`.
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

    return returncode


def idb_excepthook(type, value, tb):
    """Call an interactive debugger in post-mortem mode
    If you do `sys.excepthook = idb_excepthook`, then an interactive debugger
    will be spawned at an unhandled exception
    """
    if hasattr(sys, "ps1") or not sys.stderr.isatty():
        sys.__excepthook__(type, value, tb)
    else:
        traceback.print_exception(type, value, tb)
        print
        pdb.pm()


def syslog_excepthook(type, value, tb):
    """Send an unhandled exception to syslog
    If you do `sys.excepthook = syslog_excepthook`,
    then unhandled exceptions will be sent to syslog before the program exits.
    """

    # Note that format_exception() returns
    # "a list of strings, each ending in a newline and some containing internal newlines"
    # <https://docs.python.org/3/library/traceback.html#traceback.format_exception>
    exc = "".join(traceback.format_exception(type, value, tb))
    logger.error(f"Encountered unhandled exception and must exit :(")
    for line in exc.splitlines():
        logger.error(line)


def configure_logging(log_stderr: str, log_syslog: str = "NONE") -> None:
    """Configure logging for the command-line programs
    A convenience function that sets up logging based on the command-line arguments.
    Should only be called once.
    Params:
    * `log_stderr`: The log level for stderr, one of `progfiguration_log_levels`.
    * `log_syslog`: The log level for syslog, one of `progfiguration_log_levels`.
    """
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


def get_command_help(name: str, parser: argparse.ArgumentParser, wrap: int = 80, wrap_indent: int = 8):
    """Generate a docstring for an argparse parser that shows the help for the parser and all subparsers.
    Based on an idea from <https://github.com/pdoc3/pdoc/issues/89>
    Arguments:
    * `name`: The name of the program
    * `parser`: The parser
    * `wrap`: The number of characters to wrap the help text to (0 to disable)
    * `wrap_indent`: The number of characters to indent the wrapped text
    """

    def get_parser_help_recursive(parser: argparse.ArgumentParser, cmd: str = "", root: bool = True):
        docstring = ""
        if not root:
            docstring += "\n" + "_" * 72 + "\n\n"
        docstring += f"> {cmd} --help\n"
        docstring += parser.format_help()

        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                for subcmd, subparser in action.choices.items():
                    docstring += get_parser_help_recursive(subparser, f"{cmd} {subcmd}", root=False)
        return docstring

    docstring = get_parser_help_recursive(parser, name)

    if wrap > 0:
        wrapped = []
        # From the textwrap docs:
        # > If replace_whitespace is false,
        # > newlines may appear in the middle of a line and cause strange output.
        # > For this reason, text should be split into paragraphs
        # > (using str.splitlines() or similar) which are wrapped separately.
        for line in docstring.splitlines():
            if line:
                wrapped += textwrap.wrap(
                    line, width=wrap, replace_whitespace=False, subsequent_indent=" " * wrap_indent
                )
            else:
                wrapped += [""]
        return "\n".join(wrapped)
    else:
        return docstring


def CommaSeparatedStrList(cssl: str) -> List[str]:
    """Convert a string with commas into a list of strings

    Useful as a type= argument to argparse.add_argument()
    """
    return cssl.split(",")
