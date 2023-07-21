"""psyopsOS progfiguration module"""

import logging


"""We define a root logger here that will log any level, but no handler.

Expect that cli.py will configure handlers set to the appropriate level.
"""
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)


"""The path to the progfigsite module

This might change if eg the user passes --site-module-path to the CLI.

(Note however that this is a Python package path,
while --site-module-path is a filesystem path.)
"""
progfigsite_module_path = "progfigsite"
