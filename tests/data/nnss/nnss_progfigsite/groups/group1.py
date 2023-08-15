"""My home k3s cluster"""

group = dict(
    roles=dict(
        settz={
            "timezone": "US/Pacific",
        }
    ),
)
