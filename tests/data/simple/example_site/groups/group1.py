"""My home k3s cluster"""

from progfiguration.progfigtypes import Bunch

group = Bunch(
    roles=Bunch(
        settz={
            "timezone": "UTC",
        }
    ),
)
