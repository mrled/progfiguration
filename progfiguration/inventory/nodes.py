"""Nodes managed by progfiguration"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class InventoryNode:
    """A data structure for an inventory node."""

    address: str
    """The hostname or IP address used to connect over SSH"""

    ssh_host_fingerprint: str
    """The SSH host key fingerprint"""

    roles: Dict[str, Any]
    """Role arguments for this node.

    The key is the role name, and the value is the role argument.
    """

    user: str = "root"
    """The username used to connect over SSH"""

    sitedata: Optional[Dict[str, Any]] = None
    """Any site-specific data can be stored here.

    You can store any data you want here.
    You might include a serial number, a notes field, a location, etc.
    """

    TESTING_DO_NOT_APPLY: bool = False
    """If this is True, 'progfiguration apply' will refuse to run.

    Useful for inspecting early state in machines that run 'progfigsite apply' on boot.
    """
