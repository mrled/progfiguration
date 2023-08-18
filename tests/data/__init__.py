"""Test data"""


import configparser
import pathlib
import sys

import progfiguration
from progfiguration import logger, sitewrapper
from progfiguration.cli.util import configure_logging


class NnssTestData:
    """A bundle of test data for the NNSS progfigsite

    Properties:
    - nnss_progfigsite_path: pathlib.Path to the NNSS progfigsite package
    - invfilecfg: configparser.ConfigParser for the NNSS progfigsite inventory.conf
    - inventory: progfiguration.inventory.Inventory for the NNSS progfigsite

    """

    def __init__(self):
        configure_logging("DEBUG")
        logger.debug("Loading NNSS test data")
        # Find nnss progfigsite paths
        parent_path = pathlib.Path(__file__).parent
        nnss_path = pathlib.Path(parent_path / "nnss")

        # Place the test progfigsite package on the path
        if nnss_path.as_posix() not in sys.path:
            sys.path.insert(0, nnss_path.as_posix())

        # Set the test progfigsite package as the site package
        progfiguration.progfigsite_module_path = "nnss_progfigsite"

        self.progfigsite_path = pathlib.Path(nnss_path / "nnss_progfigsite")
        self.controller_age = pathlib.Path(nnss_path / "controller.age")

        self.progfigsite = sitewrapper.get_progfigsite()

        self.invfilecfg = configparser.ConfigParser()
        self.invfilecfg.read(sitewrapper.site_submodule_resource("", "inventory.conf"))

        # Override the controller age path to point to the test controller age,
        # no matter where it is on the filesystem.
        self.invfilecfg.set("general", "controller_age_path", str(self.controller_age))
