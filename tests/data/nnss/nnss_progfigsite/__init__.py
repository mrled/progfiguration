"""Site configuration goes here

This includes everything that is not generic to how progfiguration works,
but is specific to my hosts/roles/groups/functions/etc.
"""

from pathlib import Path

from progfiguration import sitewrapper
from progfiguration.inventory.storeimpl.agesecrets import AgeSecretFileStore
from progfiguration.inventory.invstores import HostStore


site_name = "Nevada Test Site"

# What a boring motto.
# From the Wikipedia page for Nevada Test and Training Range (military unit)
site_description = "Force for Freedom"


inventory = HostStore(sitewrapper.site_submodule_resource("", "inventory.conf"))
"""The site's inventory"""

secretstore = AgeSecretFileStore(
    # This pubkey matches the private key we keep in the package directory.
    controller_age_pubkey="age1dmxq0tws40d8npseun9azpq65smpyd2kqfyj0ytlk6m7trn7nsxqnsrag2",
    decryption_age_privkey_path_list=[
        # Let the unit tests find controller.age in this file's parent directory.
        # Normally you would not want to keep it here,
        # as it would mean your controller key is in version control.
        (Path(__file__).parent.parent / "controller.age").as_posix(),
        # An example default value, not used in our unit tests
        "/default/path/for/nodes/key.age",
    ],
)
"""The method for storing secrets."""


def mint_version() -> str:
    """Mint a new version number

    This function is called by progfiguration core to generate a version number.
    It may be called by site-specific code as well.
    It should return a string that is a valid pip version number.
    (If you are also building other packages like RPMs,
    make sure to use a version number that is valid for all of them.)
    """
    from datetime import datetime

    dt = datetime.utcnow()
    epoch = int(dt.timestamp())
    version = f"1.0.{epoch}"
    return version


def get_version() -> str:
    """Dynamically get the package version

    If we have version data injected at build time, retrieve that.
    Otherwise return a default version.

    The default version can be any valid version that conforms to your normal versioning scheme.
    A reasonable default is "0.0.1a0".
    """

    try:
        from nnss_progfigsite.builddata import version

        return version.version
    except ImportError:
        return "0.0.1a0"
