"""Progfiguration site wrapper

If the user site exists, import it.
Otherwise, import the example site.
"""

try:
    import progfigsite as site
except ImportError:
    import progfiguration.example_site as site


# # All site packages must export the following names.
# # These are the only names that are referenced by progfiguration core.
# nodes = site.nodes
# roles = site.roles
# groups = site.groups
# # sitelib = site.sitelib
# package_inventory_file = site.package_inventory_file
