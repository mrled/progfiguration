"""progfiguration root module"""

import logging


logger = logging.getLogger()
"""We define a root logger here that will log any level, but no handler.

Expect that cli.py will configure handlers set to the appropriate level.
"""
logger.setLevel(logging.NOTSET)
