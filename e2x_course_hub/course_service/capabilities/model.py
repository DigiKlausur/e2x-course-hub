from dataclasses import dataclass

from e2x_hub_rbac.auth import PermissionProtocol, Scope


@dataclass(frozen=True)
class Capability:
    """Something a user can do, and the permissions it requires.

    The capability is what users see and what gets a text in the frontend; the
    permissions are what the backend enforces. Most capabilities need a single
    permission.
    """

    # Path of the field in the response, e.g. "membership.teachingAssistants.add".
    # Only unique within the capability's scope.
    id: str
    permissions: frozenset[PermissionProtocol]

    def __post_init__(self):
        if not self.permissions:
            raise ValueError(f"Capability {self.id!r} requires no permissions")
        scopes = {permission.required_scope for permission in self.permissions}
        if len(scopes) > 1:
            raise ValueError(f"Capability {self.id!r} mixes permission scopes: {sorted(scopes)}")

    @classmethod
    def of(cls, id: str, *permissions: PermissionProtocol) -> "Capability":
        return cls(id=id, permissions=frozenset(permissions))

    @property
    def scope(self) -> Scope:
        """The level the capability applies to: the shared scope of its permissions."""
        return next(iter(self.permissions)).required_scope


@dataclass(frozen=True)
class MembershipCapabilityGroup:
    """The view/add/remove capabilities of one member list, e.g. the TAs of a term."""

    view: Capability
    add: Capability
    remove: Capability

    @classmethod
    def of(
        cls,
        prefix: str,
        *,
        list: PermissionProtocol,
        add: PermissionProtocol,
        remove: PermissionProtocol,
    ) -> "MembershipCapabilityGroup":
        return cls(
            view=Capability.of(f"{prefix}.view", list),
            add=Capability.of(f"{prefix}.add", add),
            remove=Capability.of(f"{prefix}.remove", remove),
        )

    def __iter__(self):
        return iter((self.view, self.add, self.remove))
