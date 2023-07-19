import pathlib
import subprocess
import tempfile

from progfiguration import example_site, progfigbuild, sitewrapper

from tests import PdbTestCase, pdbexc, skipUnlessAnyEnv
from tests.data import NnssTestData


class TestRun(PdbTestCase):
    @pdbexc
    @skipUnlessAnyEnv("PROGFIGURATION_TEST_SLOW_ALL", "PROGFIGURATION_TEST_SLOW_PACKAGING")
    def test_package_example_site(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pyzfile = pathlib.Path(tmpdir) / "test.pyz"
            progfigbuild.build_progfigsite_zipapp(pyzfile, pathlib.Path(example_site.__file__).parent)
            self.assertTrue(pyzfile.exists())
            result = subprocess.run([str(pyzfile), "version"], check=True, capture_output=True)
            stdout = result.stdout.decode("utf-8").strip()
            self.assertTrue("progfiguration core" in stdout)
            self.assertTrue(example_site.site_name in stdout)
            self.assertTrue(example_site.site_description in stdout)

    @pdbexc
    @skipUnlessAnyEnv("PROGFIGURATION_TEST_SLOW_ALL", "PROGFIGURATION_TEST_SLOW_PACKAGING")
    def test_package_nnss(self):
        nnss = NnssTestData()
        with tempfile.TemporaryDirectory() as tmpdir:
            pyzfile = pathlib.Path(tmpdir) / "test.pyz"
            progfigbuild.build_progfigsite_zipapp(pyzfile, nnss.nnss_progfigsite_path)
            self.assertTrue(pyzfile.exists())
            result = subprocess.run([str(pyzfile), "version"], check=True, capture_output=True)
            stdout = result.stdout.decode("utf-8").strip()
            self.assertTrue("progfiguration core" in stdout)
            self.assertTrue(sitewrapper.progfigsite.site_name in stdout)
            self.assertTrue(sitewrapper.progfigsite.site_description in stdout)
