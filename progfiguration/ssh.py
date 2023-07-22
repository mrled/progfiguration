"""SSH operations"""


import os
from pathlib import Path
import tempfile

from progfiguration.cmd import magicrun
from progfiguration.progfigtypes import AnyPathOrStr, PathOrStr


def _generate_pubkey_from_path(path: PathOrStr) -> str:
    """Generate a public key from a private key"""
    if not isinstance(path, str):
        path = path.as_posix()
    return magicrun(["ssh-keygen", "-y", "-f", path], print_output=False).stdout.read()


def _generate_pubkey_from_string(key: str) -> str:
    """Generate a public key from a private key"""
    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        key_path = tmpdir / "key"
        key_path.write_text(key)
        key_path.chmod(0o600)
        return _generate_pubkey_from_path(key_path)


def generate_pubkey(privkey: AnyPathOrStr) -> str:
    """Generate a public key from a private key

    The private key can be a string containing the key itself,
    or a path to a file containing the key.
    If a path, it can be a string or one of several Path-like types.
    """
    if isinstance(privkey, str):
        if os.path.exists(privkey):
            # If it's a string of a path that exists, read from that file
            return _generate_pubkey_from_path(Path(privkey))
        else:
            # Otherwise, treat it as a string containing the key itself
            return _generate_pubkey_from_string(privkey)
    elif isinstance(privkey, Path):
        # If it's a real Path, we can just read from that file
        return _generate_pubkey_from_path(privkey)
    else:
        # But if it's another kind of Path-like object, we need to read its contents first,
        # because ssh-keygen doesn't know how to read from zipfiles etc
        return _generate_pubkey_from_string(privkey.read_text())
