"""Age secret file store.

Store progfiguration secrets as files.
Each secret is encrypted by an Age key.

Wrap the age binary to encrypt and decrypt secret values
"""


from dataclasses import dataclass
import datetime
import json
from pathlib import Path
import subprocess
from typing import Any, Dict, List, Literal, Optional

from progfiguration import logger, sitewrapper
from progfiguration.inventory.invstores import get_inherited_secret
from progfiguration.inventory.invstores import HostStore
from progfiguration.inventory.invstores import SecretReference
from progfiguration.inventory.invstores import Secret, SecretStore


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
    def generate(cls, path: Optional[Path] = None) -> "AgeKey":
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
class AgeSecretReference(SecretReference):
    """A reference to a secret by name

    This is a wrapper type that allows us to pass around a reference to a secret
    without having to know the secret's value.
    """

    name: str
    """The name of the secret"""

    def dereference(
        self,
        nodename: str,
        inventory: HostStore,
        secretstore: SecretStore,
    ) -> Any:
        secret = get_inherited_secret(inventory, secretstore, nodename, self.name)
        value = secret.decrypt()
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


class AgeSecretFileStore(SecretStore):
    """Age secret file store for progfiguration inventories.

    Store progfiguration secrets as files.
    Each secret is encrypted by an Age key.
    """

    controller_age_pubkey: str
    """The controller's age public key"""

    _cache: Dict[str, Dict[str, Dict[str, Secret]]]
    """An in-memory cache.

    self._cache[collection][name] = {secretname: Secret}
    """

    decryption_age_privkey_path: str = ""
    """If this is not empty, use this path to an age private key to decrypt secrets.

    During initialization,
    this is set to the first item in decryption_age_privkey_path_list that exists.
    Can be (re-)set after initialization.

    TODO: how will the cli code in core allow setting this at runtime?
    """

    def __init__(
        self,
        controller_age_pubkey: str,
        decryption_age_privkey_path_list: Optional[List[str]] = None,
    ):
        """Initializer parameters:

        ``controller_age_pubkey``:
            The controller's age public key.

        ``decryption_age_privkey_path_list``:
            Paths to an age private key to decrypt secrets.
            Tried in order provided.
            If none are found, we cannot decrypt secrets.
        """
        self.controller_age_pubkey = controller_age_pubkey
        for item in decryption_age_privkey_path_list or []:
            if Path(item).exists():
                logger.debug(f"AgeSecretFileStore: Found decryption key at {item}")
                self.decryption_age_privkey_path = item
                break
            else:
                logger.debug(f"AgeSecretFileStore: Could not find decryption key at {item}")

        self._cache = {"node": {}, "group": {}, "special": {}}

    def _get_secrets_file(self, collection: Literal["node", "group", "special"], name: str) -> Path:
        if collection == "node":
            return sitewrapper.site_submodule_resource("nodes", f"{name}.secrets.json")
        elif collection == "group":
            return sitewrapper.site_submodule_resource("groups", f"{name}.secrets.json")
        else:
            return sitewrapper.site_submodule_resource("", f"{name}.secrets.json")

    def _load_secrets(self, collection: Literal["node", "group", "special"], name: str) -> Dict[str, Secret]:
        """Load a secrets from a secret store.

        Cache them in memory for future use.
        """
        secrets_file = self._get_secrets_file(collection, name)
        if secrets_file.exists():
            with secrets_file.open() as fp:
                contents = json.load(fp)
                self._cache[collection][name] = {}
                for k, v in contents.items():
                    self._cache[collection][name][k] = AgeSecret(v, self.decryption_age_privkey_path)
        else:
            self._cache[collection][name] = {}
        return self._cache[collection][name]

    def _save_secrets(self, collection: Literal["node", "group", "special"], name: str):
        """Save a secrets to a secret store.

        Save them to disk.
        """
        secrets_file = self._get_secrets_file(collection, name)
        with secrets_file.open("w") as fp:
            json.dump(self._cache[collection][name], fp, indent=2, sort_keys=True)

    def list_secrets(self, collection: Literal["node", "group", "special"], name: str) -> List[str]:
        """List secrets."""
        entity_secrets = self._load_secrets(collection, name)
        return list(entity_secrets.keys())

    def get_secret(self, collection: Literal["node", "group", "special"], name: str, secret_name: str) -> Secret:
        """Retrieve a secret from the secret store.

        This operation returns an opaque Secret type.
        The secret does not have to be decrypted yet,
        but can be, depending on the Secret implementation.
        """
        entity_secrets = self._load_secrets(collection, name)
        return entity_secrets[secret_name]

    def set_secret(
        self,
        inventory: HostStore,
        name: str,
        value: str,
        nodes: List[str],
        groups: List[str],
        controller_key: bool,
        store: bool = False,
    ):
        """Encrypt a secret for some list of nodes and groups.

        Always encrypt for the controller so that it can decrypt too.

        We assume this only ever happens on the controller.
        """

        recipients = nodes.copy()

        for group in groups:
            recipients += inventory.group_members[group]
        recipients = list(set(recipients))

        nmods = [inventory.node(n) for n in recipients]
        pubkeys = [nm.node.age_pubkey for nm in nmods]

        # We always encrypt for the controller when storing, so that the controller can decrypt too
        if controller_key or store:
            pubkeys += [self.controller_age_pubkey]

        encrypted_value = encrypt(value, pubkeys)
        logger.debug(f"Encrypted secret {name} for nodes: {recipients} with public keys: {pubkeys}")

        if store:
            for node in nodes:
                if node not in self._cache["node"]:
                    self._cache["node"][node] = {}
                self._cache["node"][node][name] = AgeSecret(encrypted_value, self.decryption_age_privkey_path)
            for group in groups:
                if group not in self._cache["group"]:
                    self._cache["group"][group] = {}
                self._cache["group"][group][name] = AgeSecret(encrypted_value, self.decryption_age_privkey_path)
            if controller_key:
                if name not in self._cache["special"]["controller"]:
                    self._cache["special"]["controller"] = {}
                self._cache["special"]["controller"][name] = AgeSecret(
                    encrypted_value, self.decryption_age_privkey_path
                )

        return encrypted_value
