"""Test data"""


import configparser
import pathlib

from progfiguration import sitewrapper
from progfiguration.inventory import Inventory


class NnssTestData:
    """A bundle of test data for the NNSS progfigsite

    Properties:
    - nnss_progfigsite_path: pathlib.Path to the NNSS progfigsite package
    - invfilecfg: configparser.ConfigParser for the NNSS progfigsite inventory.conf
    - inventory: progfiguration.inventory.Inventory for the NNSS progfigsite

    """

    def __init__(self):
        # Find nnss progfigsite paths
        parent_path = pathlib.Path(__file__).parent
        nnss_path = pathlib.Path(parent_path / "nnss")
        self.nnss_progfigsite_path = pathlib.Path(nnss_path / "nnss_progfigsite")
        nnss_controller_age = pathlib.Path(nnss_path / "controller.age")

        # Place the test progfigsite package on the path, and set it as the site package
        sitewrapper.set_site_module_filepath(str(self.nnss_progfigsite_path))

        self.invfilecfg = configparser.ConfigParser()
        self.invfilecfg.read(sitewrapper.site_submodule_resource("", "inventory.conf"))

        # Override the controller age path to point to the test controller age,
        # no matter where it is on the filesystem.
        self.invfilecfg.set("general", "controller_age_path", str(nnss_controller_age))

        self.inventory = Inventory(self.invfilecfg, str(nnss_controller_age))
