"""Example simple role"""

from dataclasses import dataclass
import shutil


from progfiguration.cmd import run
from progfiguration.inventory.roles import ProgfigurationRole


@dataclass(kw_only=True)
class Role(ProgfigurationRole):

    timezone: str

    def apply(self):
        run(f"apk add tzdata")

        shutil.copyfile(f"/usr/share/zoneinfo/{self.timezone}", "/etc/localtime")
        with open(f"/etc/timezone", "w") as tzfp:
            tzfp.write(self.timezone)

        run("rc-service ntpd restart")