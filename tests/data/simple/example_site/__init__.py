"""Site configuration goes here

This includes everything that is not generic to how progfiguration works,
but is specific to my hosts/roles/groups/functions/etc.
"""

from progfiguration import sitewrapper
from progfiguration.sitehelpers import siteversion
from progfiguration.sitehelpers.invconf import hosts_conf, secrets_conf


site_name = "example_site"
"""The name of the site package

This must match the name of the site package defined in pyproject.toml.
"""

site_description = "This site is bundled with progfiguration core as an example"
"""The description of the site"""

# The progfigsite package must be set before calling anything else from progfiguration core.
sitewrapper.set_progfigsite_by_module_name(site_name)

hoststore = hosts_conf("inventory.conf")
"""The hoststore for the site

The :meth:`progfiguration.sitehelpers.invconf.hosts_conf` function
returns a :class:`progfiguration.sitehelpers.invconf.MemoryHostStore`.
The path we pass to it can be included in the site package
and found relative to the site package root.
"""

secretstore = secrets_conf("inventory.conf")
"""The secretstore for the site

The :meth:`progfiguration.sitehelpers.invconf.secrets_conf` function
returns a :class:`progfiguration.sitehelpers.invconf.AgeSecretStore`.
Note that we pass it the same config file -- it reads different sections.
"""


mint_version = siteversion.mint_version_factory_from_epoch(major=1, minor=0)
"""A function that generates a new version when it's called.

Set it from :meth:`sitehelpers.siteversion.mint_version_factory_from_epoch`,
which returns a ``mint_version()`` implementation
that returns f"{maj}.{min}.{epoch}".

Sites can write their own ``mint_version()`` if they wish,
perhaps pulling the version from a build number in a CI system.
"""
