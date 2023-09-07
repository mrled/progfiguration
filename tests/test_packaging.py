import pathlib
import tempfile

from progfiguration import progfigbuild
from progfiguration.cmd import magicrun

from tests import PdbTestCase, pdbexc, skipUnlessAnyEnv, verbose_test_output
from tests.data import nnss_test_data


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
        with nnss_test_data as nnss, tempfile.TemporaryDirectory() as tmpdir:
            pyzfile = pathlib.Path(tmpdir) / "test.pyz"
            progfigbuild.build_progfigsite_zipapp(nnss.progfigsite_path, nnss.progfigsite_name, pyzfile)
            self.assertTrue(pyzfile.exists())
            result = magicrun([str(pyzfile), "version"], print_output=verbose_test_output(), check=False)
            stdout = result.stdout.read().strip()
            self.assertTrue(result.returncode == 0)
            self.assertTrue("progfiguration core" in stdout)
            self.assertTrue("nss_progfigsite" in stdout)
            self.assertTrue(nnss.progfigsite.site_description in stdout)
