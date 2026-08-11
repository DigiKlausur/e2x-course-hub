from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, model_validator

from ..errors import ImageFamilyNotFoundError, ImageTagNotFoundError, ResourceTierNotFoundError
from ..utils import load_yaml
from .enums import SpawnRole

# ── Selections (stored per course/term) ─────────────────────────────


class ImageSelection(BaseModel):
    family: str
    tag: Optional[str] = None

    def with_fallback(self, fallback: "ImageSelection") -> "ImageSelection":
        return ImageSelection(
            family=self.family if self.family is not None else fallback.family,
            tag=self.tag if self.tag is not None else fallback.tag,
        )


class ResourceSelection(BaseModel):
    student: Optional[str] = None
    grader: Optional[str] = None

    def with_fallback(self, fallback: "ResourceSelection") -> "ResourceSelection":
        return ResourceSelection(
            student=self.student if self.student is not None else fallback.student,
            grader=self.grader if self.grader is not None else fallback.grader,
        )


# ── Resolved runtime types ──────────────────────────────────────────


class Image(BaseModel):
    name: str
    tag: str
    pullPolicy: str = "IfNotPresent"

    @property
    def full_image_name(self) -> str:
        return f"{self.name}:{self.tag}"


class Resources(BaseModel):
    cpu_guarantee: float = 0.001
    cpu_limit: float = 2.0
    mem_guarantee: str = "1.0G"
    mem_limit: str = "2.0G"


class Runtime(BaseModel):
    image: Image
    resources: Resources
    environment: Dict[str, str | float | int | bool] = {}

    def to_kubespawner_override(self) -> Dict[str, Any]:
        overrides: Dict[str, Any] = {
            "image": self.image.full_image_name,
            "image_pull_policy": self.image.pullPolicy,
            **self.resources.model_dump(),
            "environment": {k: str(v) for k, v in self.environment.items()},
        }
        return overrides


# ── Image catalog ────────────────────────────────────────────────────


class TagInfo(BaseModel):
    status: Literal["active", "deprecated", "removed"]
    message: Optional[str] = None


class ImageFlavors(BaseModel):
    student: str
    grader: str


class ImageFamily(BaseModel):
    display_name: str
    description: str
    default_tag: str
    pullPolicy: Optional[str] = None
    registry: Optional[str] = None
    images: ImageFlavors
    tags: dict[str, TagInfo]

    @model_validator(mode="after")
    def _validate_default_tag(self) -> "ImageFamily":
        if self.default_tag not in self.tags:
            raise ValueError(
                f"default_tag '{self.default_tag}' not in tags: {list(self.tags.keys())}"
            )
        return self


class ImageCatalog(BaseModel):
    default_registry: str
    default_pull_policy: Optional[str] = None
    default_family: str
    families: dict[str, ImageFamily]

    @model_validator(mode="after")
    def _validate_default_family(self) -> "ImageCatalog":
        if self.default_family not in self.families:
            raise ValueError(
                f"default_family '{self.default_family}' not in families: "
                f"{list(self.families.keys())}"
            )
        return self

    def assert_image_selection_exists(self, selection: ImageSelection) -> None:
        family_name = selection.family or self.default_family
        family = self.families.get(family_name)
        if not family:
            raise ImageFamilyNotFoundError(family_name)
        tag = selection.tag or family.default_tag
        if tag not in family.tags:
            raise ImageTagNotFoundError(family_name, tag)


# ── Resource catalog ─────────────────────────────────────────────────


class ResourceTier(BaseModel):
    display_name: str
    description: str
    warning: Optional[str] = None
    resources: Resources


class ResourceTiers(BaseModel):
    default_tier: str
    tiers: dict[str, ResourceTier]

    @model_validator(mode="after")
    def _validate_default_tier(self) -> "ResourceTiers":
        if self.default_tier not in self.tiers:
            raise ValueError(
                f"default_tier '{self.default_tier}' not in tiers: {list(self.tiers.keys())}"
            )
        return self

    def get_resources_for_tier(self, tier_name: Optional[str] = None) -> Resources:
        name = tier_name or self.default_tier
        if name not in self.tiers:
            raise ValueError(f"Tier '{name}' not found. Available: {list(self.tiers.keys())}")
        return self.tiers[name].resources


class ResourceTiersByRole(BaseModel):
    student: ResourceTiers
    grader: ResourceTiers

    def assert_resource_selection_exists(self, selection: ResourceSelection) -> None:
        for role_name in ("student", "grader"):
            tier_name = getattr(selection, role_name)
            if tier_name:
                tiers = getattr(self, role_name)
                if tier_name not in tiers.tiers:
                    raise ResourceTierNotFoundError(tier_name, role_name)


# ── Top-level catalog ────────────────────────────────────────────────


class InfrastructureCatalog(BaseModel):
    image_catalog: ImageCatalog
    resource_tiers: ResourceTiersByRole

    @classmethod
    def from_config_file(cls, file_path: str) -> "InfrastructureCatalog":
        return cls(**load_yaml(file_path))

    def _get_resources_for_role(
        self, role: SpawnRole, tier_name: Optional[str] = None
    ) -> Resources:
        return getattr(self.resource_tiers, role.value).get_resources_for_tier(tier_name)

    def _get_image_for_role(
        self,
        role: SpawnRole,
        family_name: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> Optional[Image]:
        family_name = family_name or self.image_catalog.default_family
        family = self.image_catalog.families.get(family_name)
        if not family:
            return None
        registry = family.registry or self.image_catalog.default_registry
        pull_policy = family.pullPolicy or self.image_catalog.default_pull_policy or "IfNotPresent"
        image_name = f"{registry}/{getattr(family.images, role.value)}"
        image_tag = tag or family.default_tag
        return Image(name=image_name, tag=image_tag, pullPolicy=pull_policy)

    def assert_image_selection_exists(self, selection: ImageSelection) -> None:
        self.image_catalog.assert_image_selection_exists(selection)

    def assert_resource_selection_exists(self, selection: ResourceSelection) -> None:
        self.resource_tiers.assert_resource_selection_exists(selection)

    def get_resources_for_role(
        self, role: SpawnRole, resource_selection: ResourceSelection
    ) -> Resources:
        tier_name = getattr(resource_selection, role.value)
        return self._get_resources_for_role(role, tier_name)

    def get_image_for_role(
        self, role: SpawnRole, image_selection: ImageSelection
    ) -> Optional[Image]:
        return self._get_image_for_role(role, image_selection.family, image_selection.tag)

    def get_default_image_selection(self) -> ImageSelection:
        default = self.image_catalog.default_family
        family = self.image_catalog.families[default]
        return ImageSelection(family=default, tag=family.default_tag)

    def get_default_resource_selection(self) -> ResourceSelection:
        return ResourceSelection(
            student=self.resource_tiers.student.default_tier,
            grader=self.resource_tiers.grader.default_tier,
        )
