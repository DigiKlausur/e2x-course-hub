from pydantic import BaseModel, Field


class MembershipCollectionResponse(BaseModel):
    # Required rather than defaulted: the router always supplies it, and a
    # ``default_factory`` cannot be represented in the OpenAPI schema, so it would
    # show up as an optional field in the generated client types.
    usernames: list[str]


class MembershipPatch(BaseModel):
    """Request body for add/remove membership operations."""

    add: list[str] = Field(default_factory=list, description="Usernames to add.")
    remove: list[str] = Field(default_factory=list, description="Usernames to remove.")
