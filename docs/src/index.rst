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
It provides:

*   A way to write code to configure your infrastructure.
*   A simple standard library for functions like writing to files idempotently.
*   Judicious use of dependencies:
    remote deployments typically use SSH,
    the default secret storage mechanism uses `Age <https://github.com/FiloSottile/age>`_,
    and building/development use well supported third party Python libraries.
*   A command-line interface for running your configuration.
*   A nice package building experience that assmebles your code into a single executable.

The whole point of ``progfiguration`` is that your configuration is just Python code.
You can use any Python library you want, and you can use any Python code you want.

And you don't have to fight the declarative model when all you want to do is set an intermediate value to a variable or write a loop.

Do you...

* ...wish you could write a real program, even multiple lines, instead of toiling in the YAML mines?
* ...hate running widely available stable software supported by well-funded corporations and large communities?

``progfiguration`` **is for you!**

Availability
------------

*   The source code is available on GitHub at `mrled/progfiguration <https://github.com/mrled/progfiguration>`_.
*   Releases are on PyPI as `progfiguration <https://pypi.org/project/progfiguration/>`_.
*   Progfiguration is available under the `MIT license <https://github.com/mrled/progfiguration/blob/master/LICENSE>`_.
*   Written by `Micah R Ledbetter <http://me.micahrl.com>`_.

Patches and bug reports are welcome!
If you use ``progfiguration`` for your own infrastructure, I'd love to hear about it,
and you're welcome to add yourself to the :doc:`list of users </appendix/users>` list.

A guided tour of the documentation
----------------------------------

Read :ref:`progfiguration-getting-started` first.
It will walk you through installing ``progfiguration`` and building out your *site*,
which is the directory (usually in a Git repository) that contains your inventory.
When you're exploring, you might be interested in the :ref:`command help <commands>` reference,
and the :ref:`progfigsite API <progfigsite>` that lists your site package must implement.
You might also want to read :ref:`for-ansible-users`,
if you're familiar with Ansible.
See :ref:`whyuse` for some scenarios that ``progfiguration`` was designed to handle well,
and :ref:`progfiguration-design` to read about design principles and hypotheses.

Table of Contents
-----------------

.. This `toctree` directive is required for the docs to build.
    Every file in the `docs/` directory must be listed here,
    or in a `toctree` directive in one of the files listed here.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting-started/index.rst
   user-reference/index.rst
   design/index.rst
   appendix/index.rst


Indices
^^^^^^^

* :ref:`Module index <modindex>`, containing documentation for every Python module
* :ref:`Complete index <genindex>`, containing a flat list of every function, variable, class, module, etc on a single page
