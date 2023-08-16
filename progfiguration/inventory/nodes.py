"""Nodes managed by progfiguration"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class InventoryNode:
    """A data structure for an inventory node."""

    address: str
    """The hostname or IP address used to connect over SSH"""

    age_pubkey: str
    """The Age public key for encrypting secrets"""

    ssh_host_fingerprint: str
    """The SSH host key fingerprint"""

    roles: Dict[str, Any]
    """Role arguments for this node.

    The key is the role name, and the value is the role argument.
    """

    user: str = "root"
    """The username used to connect over SSH"""

    age_key_path: Optional[str] = None
    """The path to the Age private key for decrypting secrets.

    If this is not present, fall back to the default value specified in the inventory.conf.
    """

    sitedata: Optional[Dict[str, Any]] = None
    """Any site-specific data can be stored here.

    You can store any data you want here.
    You might include a serial number, a notes field, a location, etc.
    """

    TESTING_DO_NOT_APPLY: bool = False
    """If this is True, 'progfiguration apply' will refuse to run.

    Useful for inspecting early state in machines that run 'progfigsite apply' on boot.
    """
