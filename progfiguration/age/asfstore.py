"""asfstore: Age secret file store.

Store progfiguration secrets as files.
Each secret is encrypted by an Age key.
"""


import json
from pathlib import Path
from typing import Dict, List, Literal, Optional

from progfiguration import logger, sitewrapper
from progfiguration.age import AgeSecret, encrypt
from progfiguration.inventory import Inventory, Secret, SecretStore
from progfiguration.progfigtypes import AnyPathOrStr


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
        inventory: Inventory,
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
