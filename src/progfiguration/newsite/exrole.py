"""Example simple role"""

from dataclasses import dataclass
import shutil


from progfiguration.cmd import magicrun
from progfiguration.inventory.roles import ProgfigurationRole


@dataclass(kw_only=True)
class Role(ProgfigurationRole):
    """Set the timezone on an Alpine Linux host."""

    timezone: str

    def apply(self):
        magicrun(f"apk add tzdata")

        shutil.copyfile(f"/usr/share/zoneinfo/{self.timezone}", "/etc/localtime")
        with open(f"/etc/timezone", "w") as tzfp:
            tzfp.write(self.timezone)

        magicrun("rc-service ntpd restart")
