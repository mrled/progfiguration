``progfiguration`` documentation
================================

``progfiguration`` is **prog**\ ramatic con\ **figuration** for your infrastructure.
It's *infrastructure as code*, but like, actual *code*.

.. note::

    This project is currently *extremely alpha*.
    It's subject to change, even more than most software.
    And, as we know, all change is loss.
    Rely on this project and imperil not just your infrastructure, but your emotional wellbeing.

Where other configuration management tools require learning a new abstraction on top of the configuration changes you want to make,
``progfiguration`` lets you *just write Python* to configure your infrastructure.
You can write a role, which applies to a server, like this:

.. code-block:: python

    from dataclasses import dataclass
    from pathlib import Path
    import textwrap

    from progfiguration.cmd import magicrun
    from progfiguration.inventory.roles import ProgfigurationRole

    @dataclass(kw_only=True)
    class Role(ProgfigurationRole):

        role_root_dir: Path
        username: str = "service-user"
        groupname: str = "service-group"

        @property
        def servicedir(self):
            return self.role_root_dir / "your-service"

        def apply(self):
            magicrun("dnf install -y your-service")
            self.localhost.makedirs(self.servicedir, "root", "root", 0o755)
            service_cfg = textwrap.dedent(
                f"""\
                    user = {username}
                    group = {groupname}
                    config = however you configure this thing, idk man its ur service
                """
            )
            self.localhost.set_file_contents(self.servicedir / "config", "your-service config", "root", "root", 0o644)
            magicrun("systemctl enable your-service")

        def results(self):
            return {
                "servicedir": self.servicedir,
            }

The whole point of ``progfiguration`` is that your configuration is just Python code.
You can use any Python library you want, and you can use any Python code you want.

Do you...

* ...want to write a for loop in your configuration management?
* ...wish you could write a real program, even multiple lines, when toiling in the YAML mines?
* ...hate running widely available stable software supported by well-funded corporations and large communities?

``progfiguration`` **is for you!**


.. This `toctree` directive is required for the docs to build.
    Every file in the `docs/` directory must be listed here,
    or in a `toctree` directive in one of the files listed here.

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting-started/index.rst
   commands/index.rst
   progfigsite/index.rst
   design/index.rst
   for-ansible-users/index.rst
   experiments/index.rst
   lore/index.rst
   appendix/index.rst


Indices
-------

* :ref:`Module index <modindex>`, containing documentation for every Python module
* :ref:`Complete index <genindex>`, containing a flat list of every function, variable, class, module, etc on a single page
