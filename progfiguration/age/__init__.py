"""A wrapper for the age binary to encrypt and decrypt secret values

Progfiguration uses age for secret management.
All nodes must have an age keypair.
"""

from dataclasses import dataclass
import datetime
import pathlib
import subprocess
from typing import Any, List, Optional

from progfiguration.inventory import Secret


class AgeParseException(Exception):
    pass


class MissingAgeKeyException(Exception):
    pass


class AgeKey:
    """An age keypair

    Attributes:
        secret: The secret key
        public: The public key
        created: The datetime the key was created
    """

    def __init__(self, secret: str, public: str, created: datetime.datetime):
        self.secret = secret
        self.public = public
        self.created = created

    @classmethod
    def from_output(cls, output: str) -> "AgeKey":
        """Parse the output of age-keygen into an AgeKey

        Here's example output from age-keygen -y:

            # created: 2022-09-28T16:01:22-05:00
            # public key: age14e42u048nehghjj3ch9mmnkdh4nsujn774klqxn02mznppx3gflsuj6y5m
            AGE-SECRET-KEY-1ASKGXED4DVGUH7SA50DHE2UHAYQ00PV87N2RQ5J5S6AUN9MLNSGQ3TKFGJ

        This function parses that output and returns an AgeKey object.
        """
        outlines = [l for l in output.split("\n") if l]
        if len(outlines) == 3:
            created = datetime.datetime.fromisoformat(outlines[0][11:])
            public = outlines[1][14:]
            secret = outlines[2]
        elif len(outlines) == 1:
            secret = outlines[0]
            result = subprocess.run(["age-keygen", "-y"], input=secret.encode(), check=True, capture_output=True)
            public = result.stdout.decode()
            created = datetime.datetime.now()
        else:
            raise AgeParseException(f"Could not parse age output")
        return cls(secret, public, created)

    @classmethod
    def generate(cls, path: Optional[pathlib.Path] = None) -> "AgeKey":
        """Generate a new age keypair using the age-keygen binary"""
        result = subprocess.run(["age-keygen"], check=True, capture_output=True)
        output = result.stdout.decode()
        newkey = cls.from_output(output)
        if path:
            with path.open("w") as fp:
                fp.write(output)
        return newkey

    @classmethod
    def from_file(cls, path: str) -> "AgeKey":
        """Load an age keypair from a file"""
        with open(path) as fp:
            content = fp.read()
        try:
            return cls.from_output(content)
        except AgeParseException:
            raise AgeParseException(f"Could not parse age key file at {path}")


@dataclass
class AgeSecret(Secret):
    """An age-encrypted secret value"""

    secret: str
    """The encrypted secret value"""

    privkey_path: Optional[str]
    """The path to the private key.

    If this is None, then the secret cannot be decrypted.
    """

    def decrypt(self) -> str:
        """Decrypt the secret."""
        return decrypt(self.secret, self.privkey_path)


@dataclass
class AgeSecretReference:
    """A reference to a secret by name

    This is a wrapper type that allows us to pass around a reference to a secret
    without having to know the secret's value.

    This is not a subclass of
    :class:`progfiguration.inventory.roles.RoleArgumentReference`
    because that creates an import loop,
    but it implements dereference() and that's what matters.
    """

    name: str
    """The name of the secret"""

    def dereference(
        self,
        nodename: str,
        inventory: "Inventory",  # type: ignore
    ) -> Any:
        secret = inventory.get_inherited_node_secrets(nodename)[self.name]
        value = secret.decrypt(inventory.age_path)
        return value


def encrypt(value: str, pubkeys: List[str]):
    """Encrypt a value to a list of public age keys"""
    age_cmd = ["age", "--armor"]
    for pubkey in pubkeys:
        age_cmd.append("--recipient")
        age_cmd.append(pubkey)
    proc = subprocess.run(age_cmd, input=value.encode(), check=True, capture_output=True)
    return proc.stdout.decode()


def decrypt(value: str, privkey_path: Optional[str]) -> str:
    """Decrypt an encrypted age value"""
    if not privkey_path:
        raise MissingAgeKeyException
    proc = subprocess.run(
        ["age", "--decrypt", "--identity", privkey_path],
        input=value.encode(),
        check=True,
        capture_output=True,
    )
    return proc.stdout.decode()
