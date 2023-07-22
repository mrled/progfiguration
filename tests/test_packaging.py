import pathlib
import subprocess
import tempfile

from progfiguration import progfigbuild, sitewrapper

from tests import PdbTestCase, pdbexc, skipUnlessAnyEnv
from tests.data import NnssTestData


class TestRun(PdbTestCase):

    # TODO: re-enable example_site tests, make them work like NNSS
    # @pdbexc
    # @skipUnlessAnyEnv("PROGFIGURATION_TEST_SLOW_ALL", "PROGFIGURATION_TEST_SLOW_PACKAGING")
    # def test_package_example_site(self):
    #     with tempfile.TemporaryDirectory() as tmpdir:
    #         pyzfile = pathlib.Path(tmpdir) / "test.pyz"
    #         progfigbuild.build_progfigsite_zipapp(pyzfile).parent)
    #         self.assertTrue(pyzfile.exists())
    #         result = subprocess.run([str(pyzfile), "version"], check=True, capture_output=True)
    #         stdout = result.stdout.decode("utf-8").strip()
    #         self.assertTrue("progfiguration core" in stdout)
    #         self.assertTrue(example_site.site_name in stdout)
    #         self.assertTrue(example_site.site_description in stdout)

    @pdbexc
    @skipUnlessAnyEnv(["PROGFIGURATION_TEST_SLOW_ALL", "PROGFIGURATION_TEST_SLOW_PACKAGING"])
    def test_package_nnss(self):
        nnss = NnssTestData()
        with tempfile.TemporaryDirectory() as tmpdir:
            pyzfile = pathlib.Path(tmpdir) / "test.pyz"
            progfigbuild.build_progfigsite_zipapp(pyzfile)
            self.assertTrue(pyzfile.exists())
            result = subprocess.run([str(pyzfile), "version"], check=True, capture_output=True)
            stdout = result.stdout.decode("utf-8").strip()
            self.assertTrue("progfiguration core" in stdout)
            self.assertTrue("Nevada Test Site" in stdout)
            self.assertTrue(sitewrapper.get_progfigsite().site_description in stdout)
