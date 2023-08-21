"""Test data"""

import pathlib
from typing import Any, Dict, Optional

from progfiguration import logger, sitewrapper
from progfiguration.cli.util import configure_logging


class ProgfigsiteTestData:
    """A context manager for loading a progfigsite for testing

    Properties:

    ``progfigsite_name``
        The name of the progfigsite Python module

    ``progfigsite_path``
        The filesystem path to the progfigsite

    ``progfigsite``
        The progfiguration.progfigsite.Progfigsite for the progfigsite

    ``related_data``
        A dictionary of related data for the progfigsite
    """

    def __init__(
        self, progfigsite_name: str, progfigsite_path: pathlib.Path, related_data: Optional[Dict[str, Any]] = None
    ):
        configure_logging("DEBUG")
        logger.debug(f"Loading {progfigsite_name} test data")
        self.progfigsite_name = progfigsite_name
        self.progfigsite_path = progfigsite_path
        self.related_data = related_data or {}

        # Save the current sitewrapper cache (this is a hack, but that's ok for testing)
        self.sitewrapper_cache = sitewrapper._sitewrapper_cache.copy()

    def __enter__(self):
        self.progfigsite = sitewrapper.set_progfigsite_by_filepath(self.progfigsite_path, self.progfigsite_name)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Once we exit the context manager, restore the sitewrapper cache
        sitewrapper._sitewrapper_cache = self.sitewrapper_cache


simple_example_test_data = ProgfigsiteTestData(
    "example_site", pathlib.Path(__file__).parent / "simple" / "example_site"
)
nnss_test_data = ProgfigsiteTestData(
    "nnss_progfigsite",
    pathlib.Path(__file__).parent / "nnss" / "nnss_progfigsite",
    related_data={"controller_age": pathlib.Path(__file__).parent / "nnss" / "controller.age"},
)
