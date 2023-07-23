"""progfiguration root module"""

import logging


logger = logging.getLogger()
"""We define a root logger here that will log any level, but no handler.

Expect that cli.py will configure handlers set to the appropriate level.
"""
logger.setLevel(logging.NOTSET)


progfigsite_module_path = "progfigsite"
"""The path to the progfigsite module

This might change if eg the user passes --site-module-path to the CLI.

(Note however that this is a Python package path,
while --site-module-path is a filesystem path.)
"""
