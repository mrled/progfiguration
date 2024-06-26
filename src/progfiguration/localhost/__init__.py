"""What the nodes have to say about themselves"""

import os
from pathlib import Path
import shutil
import string
import subprocess
import tempfile
from typing import Any, Dict, List, Optional

from progfiguration import temple
from progfiguration.cmd import magicrun
from progfiguration.localhost.localusers import LocalhostUsers
from progfiguration.progfigtypes import AnyPathOrStr, PathOrStr


class LocalhostLinux:
    """An interface to localhost running Linux.

    Maintains a cache of files it has read before.

    Generally, roles should use the ``.localhost`` attribute of a
    `progfiguration.inventory.Inventory` object,
    rather than instantiating this class themselves.
    That said, nothing bad will happen with multiple instances of this class.
    """

    def __init__(self, nodename="localhost"):
        self.nodename = nodename
        self.users = LocalhostUsers(self)
        self._cache_files = {}

    @property
    def uptime(self) -> float:
        """Return system uptime in seconds"""
        # System uptime in seconds, and idle CPU time in seconds
        # Note that idle CPU time accounts for idle seconds per CPU, and thus may be larger than system uptime
        uptimestr, idletimestr = self.get_file_contents("/proc/uptime", refresh=True).split()
        uptime = float(uptimestr)
        return uptime

    def get_umask(self):
        """Return the umask as integer

        Only works on Linux
        ... how the fuck is this not part of the standard library?
        <https://stackoverflow.com/questions/7150826/how-can-i-get-the-default-file-permissions-in-python>
        """
        mask = None
        with open("/proc/self/status") as fd:
            for line in fd:
                if line.startswith("Umask:"):
                    mask = int(line[6:].strip(), 8)
                    break

        if not mask:
            raise Exception("Could not find umask, lol")

        return mask

    def get_file_contents(self, path: AnyPathOrStr, chomp=True, refresh=False):
        """Retrieve file contents

        path:       The path to retrieve
        chomp:      Remove leading/trailing whitespace
        refresh:    Ignore cache if any
        """
        if not isinstance(path, str):
            path = str(path)
        if refresh or path not in self._cache_files:
            with open(path) as fp:
                contents = fp.read()
        else:
            contents = self._cache_files[path]
        if chomp:
            return contents.strip()
        else:
            return contents

    def chown(self, path: PathOrStr, owner: Optional[int | str], group: Optional[int | str], recursive=False):
        """Change the owner and/or group of a file or directory

        A convenience function that can handle any combination of owner and group.
        """
        if not isinstance(path, str):
            path = str(path)
        if not owner:
            owner = -1
        shutil.chown(path, owner, group)
        if recursive:
            for root, dirs, files in os.walk(path):
                for d in dirs:
                    self.chown(os.path.join(root, d), owner, group, recursive=True)
                for f in files:
                    self.chown(os.path.join(root, f), owner, group)

    def set_file_contents(
        self,
        path: AnyPathOrStr,
        contents: str,
        owner: Optional[str] = None,
        group: Optional[str] = None,
        mode: Optional[int] = None,
        dirmode: Optional[int] = None,
    ):
        """Set the contents of a file, creating it if necessary."""
        if not isinstance(path, str):
            path = str(path)
        self.makedirs(os.path.dirname(path), owner, group, dirmode)
        if path in self._cache_files:
            del self._cache_files[path]
        with open(path, "w") as fp:
            fp.write(contents)
        self.chown(path, owner, group)
        if mode:
            os.chmod(path, mode)

    def makedirs(
        self,
        path: PathOrStr,
        owner: Optional[str] = None,
        group: Optional[str] = None,
        mode: Optional[int] = None,
    ):
        """Create a directory and its parents, with the specified owner/group/mode."""
        if isinstance(path, str):
            path = Path(os.path.abspath(path))
        if path.exists():
            return
        if not mode:
            mode = 0o0777 - self.get_umask()
        head = path.parent
        if not os.path.exists(head):
            self.makedirs(head, owner, group, mode)
        # while os.path.islink(head):
        #     head = os.readlink(head)
        if not head.is_dir():
            raise Exception(f"Path component {head} exists but it is not a directory")
        # We have to set the mode separately, as os.mkdir()'s mode argument is umasked
        # <https://stackoverflow.com/questions/37118558/python3-os-mkdir-does-not-enforce-correct-mode>
        os.mkdir(str(path))
        if mode is not None:
            path.chmod(mode)
        self.chown(path, owner, group)

    def cp(
        self,
        src: PathOrStr,
        dest: PathOrStr,
        owner: Optional[str] = None,
        group: Optional[str] = None,
        mode: Optional[int] = None,
        dirmode: Optional[int] = None,
    ):
        """Copy a file or directory, creating the destination if necessary, with the specified owner/group/mode."""

        if isinstance(src, str):
            src = Path(src)
        if isinstance(dest, str):
            dest = Path(dest)
        self.makedirs(dest.parent, owner, group, dirmode)
        if os.path.exists(str(src)):
            shutil.copy(src, dest)
        elif hasattr(src, "open"):
            if dest.is_dir():
                dest = dest.joinpath(src.name)
            with src.open("r") as srcfp:
                with dest.open("w") as destfp:
                    shutil.copyfileobj(srcfp, destfp)
        else:
            raise Exception(f"Not sure how to copy src (type: {type(src)}) at {src} (does it exist?)")
        self.chown(dest, owner, group)
        if mode:
            dest.chmod(mode)

    def _template_backend(
        self,
        template: type,
        src: PathOrStr,
        dest: PathOrStr,
        template_args: Dict[str, Any],
        owner: Optional[str] = None,
        group: Optional[str] = None,
        mode: Optional[int] = None,
        dirmode: Optional[int] = None,
    ):
        """Template a file using the appropriate backend"""
        if isinstance(dest, str):
            dest = Path(dest)
        if isinstance(src, str):
            src = Path(src)
        self.makedirs(dest.parent, owner, group, dirmode)
        with src.open() as fp:
            template_contents = template(fp.read())
        inflated = template_contents.substitute(**template_args)
        self.set_file_contents(dest, inflated, owner, group, mode)

    def template(
        self,
        src: str,
        dest: str,
        template_args: Dict[str, Any],
        owner: Optional[str] = None,
        group: Optional[str] = None,
        mode: Optional[int] = None,
        dirmode: Optional[int] = None,
    ):
        """Template a file using Python's string.Template class."""
        return self._template_backend(string.Template, src, dest, template_args, owner, group, mode, dirmode)

    def temple(
        self,
        src: str,
        dest: str,
        template_args: Dict[str, Any],
        owner: Optional[str] = None,
        group: Optional[str] = None,
        mode: Optional[int] = None,
        dirmode: Optional[int] = None,
    ):
        """Template a file using the Temple class.

        The Temple class is very similar to string.Template,
        but does not require escaping dollar sign variables,
        which are used in shell scripts and therefore pretty common in progfiguration templates.
        """
        return self._template_backend(temple.Temple, src, dest, template_args, owner, group, mode, dirmode)

    def linesinfile(
        self,
        file: PathOrStr,
        lines: List[str],
        create_owner: Optional[str] = None,
        create_group: Optional[str] = None,
        create_mode: Optional[int] = None,
        create_dirmode: Optional[int] = None,
        trailing_newline: bool = True,
    ):
        """Ensure all lines in the input list exist in a file.

        Inspired by Ansible's lineinfile module, but simpler and less featureful

        Args:
            file: The file to modify
            lines: The lines to ensure are in the file
            create_owner: If the file does not exist, create it with this owner
            create_group: If the file does not exist, create it with this group
            create_mode: If the file does not exist, create it with this mode
            create_dirmode: If the file does not exist, create its parent directory with this mode

        If the file does not exist and at least one of `create_owner` or `create_group` is specified,
        the file will be created with the specified owner and group, and the specified mode.
        """
        if isinstance(lines, str):
            lines = [lines]
        if isinstance(file, str):
            file = Path(file)
        if not file.exists():
            if create_owner or create_group:
                self.set_file_contents(file, "\n".join(lines), create_owner, create_group, create_mode, create_dirmode)
                return
            else:
                raise FileNotFoundError(f"File {file} does not exist and no owner/group specified to create it")
        oldlines = self.get_file_contents(file, refresh=True).split("\n")
        newlines = oldlines.copy()
        for line in lines:
            if line not in oldlines:
                newlines += [line]
        contents_str = "\n".join(newlines)
        if trailing_newline:
            contents_str += "\n"
        self.set_file_contents(file, contents_str)

    def touch(
        self,
        file: PathOrStr,
        owner: Optional[str] = None,
        group: Optional[str] = None,
        mode: int = 0o666,
        dirmode: Optional[int] = None,
    ):
        """Create an empty file.

        If the file already exists, update its mtime.

        Set the owner/group/mode, if specified, regardless of whether the file already exists.

        If any parent dirs do not exist, create them as owned by owner/group with specified dirmode.
        (If parent dirs do exist, do not change their owners.)
        """
        if not isinstance(file, Path):
            file = Path(file)
        if not file.parent.exists():
            self.makedirs(file.parent, owner, group, dirmode)
        file.touch(mode=mode, exist_ok=True)
        self.chown(file, owner, group)

    def get_user_primary_group(self, user: str):
        """Get the primary group for a user.

        Use the `id` command because it is POSIX compliant
        and works with non-local users and groups like LDAP etc.
        """
        result = subprocess.run(["id", "-g", "-n", user], capture_output=True, check=True)
        return result.stdout.decode().strip()

    def write_sudoers(self, path: PathOrStr, contents: str):
        """Write a sudoers file.

        The file is written to a temporary file and then moved into place.

        You can write to /etc/sudoers this way, but it is recommended to write to /etc/sudoers.d/SOMEFILE instead.
        """
        if isinstance(path, str):
            path = Path(path)
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpfile = Path(tmpdir) / "sudoers"
            self.set_file_contents(tmpfile, contents, owner="root", group="root", mode=0o640)
            validation = magicrun(["visudo", "-cf", str(tmpfile)], check=False, print_output=False)
            if validation.returncode == 0:
                self.cp(tmpfile, path, owner="root", group="root", mode=0o440)
            else:
                raise Exception(
                    f"Failed to write sudoers file {path}: validation failed with code {validation.returncode}"
                )
