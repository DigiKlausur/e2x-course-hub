from pydantic import BaseModel, Field


class MembershipCapabilities(BaseModel):
    manage: bool = False
    view: bool = False


class MembershipCollectionResponse(BaseModel):
    usernames: list[str] = Field(default_factory=list)
    capabilities: MembershipCapabilities


class MembershipPatch(BaseModel):
    """Request body for add/remove membership operations."""

    add: list[str] = Field(default_factory=list, description="Usernames to add.")
    remove: list[str] = Field(default_factory=list, description="Usernames to remove.")
