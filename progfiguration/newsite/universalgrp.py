"""The universal group

This is not a normal group.
Membership is automatic for all nodes,
and role arguments and secrets from the universal group always apply first,
while other groups have no guarantee of order.
"""

group = dict(
    roles=dict(
        settz={
            "timezone": "UTC",
        },
    ),
)
