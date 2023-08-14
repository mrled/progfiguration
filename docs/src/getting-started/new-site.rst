Creating a New Progfiguration Site
==================================

See also :doc:`/user-reference/progfigsite/index`.

1.  Install ``progfiguration`` core.

        .. code-block:: bash

            python3 -m venv venv
            . venv/bin/activate
            pip install -U pip
            pip install progfiguration

2.  Create a new site from scratch.
    The name of your package is arbitrary, you can use anything you like.

        .. code-block:: bash

            progfiguration newsite \
                --path ./progfigsite \
                --name progfigsite \
                --description "This is a new progfigsite" \

3.  Modify the copied example to match your infrastructure.

    *   Generate a new Age controller key for your site.
        Store the key somewhere safe!

        .. code-block:: bash

            age-keygen -o /path/to/controller.age

    *   Update :doc:`the inventory file </user-reference/progfigsite/inventory>` ``progfigsite/inventory.conf`` to contain the path to the controller key and its public key value.
    *   Define your :doc:`nodes </user-reference/progfigsite/nodes>` and :doc:`groups </user-reference/progfigsite/groups>` in ``progfigsite/inventory.conf``.
    *   Create files for your nodes and groups in ``progfigsite/nodes/`` and ``progfigsite/groups``.
    *   Create Age keys for each node.
        The keys should be copied to the nodes securely.
        Nodes can set their ``age_key_path`` property to the path to their key.
        The inventory configuration file can set ``node_fallback_age_path`` for a default location.
    *   Encrypt any secrets for nodes or groups with ``progfiguration encrypt``.
    *   Define your :doc:`roles </user-reference/progfigsite/roles>` in ``progfigsite/roles/``.
    *   Define functions in ``progfigsite/inventory.conf`` by setting ``node_function_map`` and ``function_role_map``.
    *   If you use any :doc:`third party dependencies </user-reference/progfigsite/defining-dependencies>`,
        set them in ``pyproject.toml`` if appropriate.

4.  Install your progfigsite package

    *   If you use any third party dependencies, install them into your venv.
    *   Install your progfigsite as editable with ``pip install -e progfigsite``

5.  Build and deploy your site

    *   ``progfiguration deploy`` will assemble your site into a zipapp and copy it over SSH to the node.
    *   ``progfiguration build`` can assemble zipapp or pip packages for manual deployment.
    *   If you deploy a zipapp manually, you can apply it with ``/path/to/progfigsite-version.pyz apply NODENAME``.
    *   If you deploy a pip file manually, you can apply it with ``progfigsite apply NODENAME``.
    *   You can write custom build code for building RPMs or other package types.
        See an example in the `psyops progfigsite <https://github.com/mrled/psyops/blob/master/progfigsite/progfigsite/cli/progfigsite_buildapk_cmd.py>`_
