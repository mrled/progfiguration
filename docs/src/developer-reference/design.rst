.. _progfiguration-design:

Progfiguration design
=====================

The design decisions that set progfiguration apart are:

* Embracing imperative programming.
* Do not require a central server, and keep all secrets (encrypted) in the Git repository.
* It's designed to fit in one person's head, and be modifyable by end users ("editable software").

Additionally:

* It should be fast to build and fast to apply changes.

In addition to those big ideas, it's also an exploration of a few topics:

* How much can we do with just Python's standard library, and no third-party dependencies?
* Python language servers in free editors provide a lot more help than
  language servers for Ansible's YAML documents or Terraform's DSL.

Imperative
----------

A primary cause in the creation of progfiguration was a frustration with limitations in declarative programs.
Often, if you can just write a program, the result is more readable, more flexible, and faster.

Some illustrations:

* In Terraform, you may be working with long strings, like time series queries.
  At a few hundred characters or so, these become hard to read.
  Intermediate variables would help a lot.
* In Ansible, you might be working with a list of dictionaries.
  You can use filters to extract or set specific values,
  but the result can be really hard to read.
  A regular program would be a huge improvement.

A declarative paradigm can work well in simple cases like repeated record instantiation,
and the simplicity in simple cases is deceiving.
Imperative programming power is worth its cost.

Looking closely, we can see stress points in declarative designs where people have built systems to work around limitations:

* ``cloud-init`` can run shell scripts for anything more complicated than users anf files.
* How many Ansible modules are full of ``command`` invocations?

It's possible that these tradeoffs are worth it, but progfiguration is an exploration in the other direction.
What if we accepted the tradeoffs of the imperative approach and just wrote programs?

No central server
-----------------

Progfiguration is designed to work with deployed packages without a central server available.
Sites can certainly talk to central servers in roles when appropriate,
but applying the configuration and even secrets management does not require it.
Hosts should be able to apply their own configuration without relying on bespoke infrastructure that each org has to maintain.

All configuration is stored in Git and every package contains configuration for every host.
Secrets that should only apply to some hosts are encrypted with ``age``.

This is part of a design philosophy that network services should be dumb pipes,
so that critical decisions and knowledge of secrets is kept only at the endpoints.
It's also a way to avoid managing a costly availability requirement of the central server.

It enables a workflow where configuration can be baked in to an OS image
and run from scratch on each boot.
You can run stateless operating systems this way.

There are tradeoffs here.
Without a central server, you can't revoke secret access without rebuilding an image.
But in exchange, you get some resiliency.

It's also optional.
Sites could compoletely eschew the secrets supported at package build time,
and write roles that call out to a central server for secrets.

Editable software
-----------------

Progfiguration is not designed as a black box with an extensive API that provides everything you need.
Instead, sites are expected to use it as a library to build their own programs;
the philosophy of `editable software <https://flak.tedunangst.com/post/on-the-usability-of-editable-software>`_.

It is supposed to fit entirely in one person's head.

We copy the core progfiguration module in to the site package every time,
but we also expect some sites to vendor the core package and modify it.
Keeping the API small makes this manageable.
At the time this is written (pre-1.0), the core pacakge is about 3200 lines of code
in just 24 Python modules.
The code designed to be called by a site's roles is less than 1000 lines.
(You don't need much code to configure a server imperatively when starting from a large standard library like Python.)

This is also why we publish this documentation.
The hope is that it makes the core code unintimidating and easy to understand.

Speed
-----

Progfiguration should be as fast as possible.
The fastest way to use it is to use the built-in zipapp support to build a single-file executable.
Running this is faster than Ansible for large roles against a single host.
**Big caveat**: We haven't tested it running on a large number of hosts at the same time.

You can also build Pip packages, but these are slower and require dependencies like ``build``.

Dependencies
------------

It's important to be very judicious about dependencies.
We have no third-party Python runtime dependencies,
and rely on only ``ssh`` and ``age`` on remote hosts.

The Python standard library is fantastic,
and frankly under-appreciated.
It's so good!

There are a few levels that might have dependencies:

Runtime Python dependencies for the site package
    Progfiguration is designed to support packages with zero runtime dependencies.
    Sites are always welcome to add dependencies as appropriate.

Runtime non-Python dependencies for the site pacakge
    We require a working Python 3.9+ runtime.
    Aside from that, ``ssh`` is required for out of the box remote deployments,
    and ``age`` is required for out of the box secrets management.
    Sites that don't need these or want to use something else can ignore these dependencies.

Runtime Python dependencies used only inside roles for the site package
    Sometimes it's worth adding a dependency for roles,
    but this can be done in the role itself,
    without requiring a package-level dependency,
    by installing the dependency before importing it in the role.

    A few dependencies worth considering in your roles:

    * Cryptographic libraries like ``cryptography`` require third party dependencies in Python.
      This is a dependency for ``requests`` too.
    * ``pytz``, if you need to deal with timezones in your roles (many users do not).

Build time dependencies for the site package
    We avoid these if we can.
    Progfiguration sites can be built as zipapp packages with no build dependencies,
    but Pip packages require build dependencies like ``build`` and ``setuptools``,
    and we encourage using ``black`` and ``mypy`` during development for a better experience.

Runtime dependencies for the core package (Python or not)
    We prohibit these.
    The core package should work for everyone without any dependencies.

Build time dependencies for the configuration package
    We use very common, well-supported tools like ``build``, ``sphinx``, ``black``, ``mypy``, etc.

Vendoring and statically including dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You may be able to vendor dependencies into your site packages,
and we encourage this when it makes sense.
Small dependencies without security implications are an obvious case to consider.

You might also statically include dependencies at build time.
(This is sort of like "static linking" in C, commonly used in Go,
but Python doesn't have a linking step.)
Rather than vendoring the dependency (by committing the source code into your repo),
you could note it as a build-time dependency and copy its code into your package when it's built.
This means updating the package is a bit less work compared to vendoring.

If you're using zipapp packages, note that only pure Python dependencies can be vendored or statically included,
see `zipapp caveats <https://docs.python.org/3/library/zipapp.html#caveats>`_.

Python language servers
-----------------------

Python language servers in IDEs are *really good*, and progfiguration takes advantage of this.
We add type hints to everything,
and language servers can tell you how to call a function and what kind of object it returns.

The high quality and amazing feature set of Python language servers is a huge change
compared to what are essentially plain text documents in Ansible and Terraform.
