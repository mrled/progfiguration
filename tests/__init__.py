import os
import pdb
from typing import List
import unittest

from progfiguration.cli.util import configure_logging


class PdbTestCase(unittest.TestCase):
    def run(self, result=None):
        """A test runner that runs the debugger if an exception is raised and PROGFIGURATION_TEST_DEBUG is set

        This catches failed tests.
        """
        if result is None:
            result = self.defaultTestResult()

        # Run the test inside a pdb session
        try:
            super(PdbTestCase, self).run(result)
        except Exception:
            if os.environ.get("PROGFIGURATION_TEST_DEBUG"):
                pdb.post_mortem(result.failures[-1][0])
            else:
                raise


def pdbexc(test_method):
    """Decorator that runs the debugger if an exception is raised and PROGFIGURATION_TEST_DEBUG is set

    This catches exceptions in code that isn't a failed test --
    exceptions in code in a test_ method, or in code that it calls.
    """

    def wrapper(*args, **kwargs):
        try:
            test_method(*args, **kwargs)
        except Exception:
            if os.environ.get("PROGFIGURATION_TEST_DEBUG"):
                pdb.post_mortem()
            else:
                raise

    return wrapper


def skipUnlessAnyEnv(envvars: List):
    """Skip a test unless any of the given environment variables are set"""
    if any(os.environ.get(envvar) for envvar in envvars):
        return lambda func: func
    return unittest.skip(
        "Skipping test unless any of the following environment variables are set: " + ", ".join(envvars)
    )


def verbose_test_output() -> bool:
    """Return whether verbose test output is enabled"""
    verbose = bool(os.environ.get("PROGFIGURATION_TEST_VERBOSE", ""))
    return verbose


if verbose_test_output():
    configure_logging("DEBUG")
