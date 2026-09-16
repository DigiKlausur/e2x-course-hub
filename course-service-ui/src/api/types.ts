/**
 * Public API types for the course service.
 *
 * These are thin aliases over `schema.d.ts`, which is generated from the
 * service's OpenAPI document — see `npm run generate:api-types`. Do not add
 * free-standing interfaces here: a shape that is not derived from the generated
 * schema can drift from the backend without the compiler noticing, which is
 * exactly what this indirection exists to prevent.
 *
 * The aliases serve two purposes beyond renaming. They give the UI stable names
 * that survive backend renames (`ImageCatalog` rather than `ImageFamilyOptions`),
 * and they restore the spawn-role keys described below.
 *
 * On `SpawnRoleMap`: the backend types these maps as `dict[SpawnRole, ...]` and
 * FastAPI faithfully emits `propertyNames: {$ref: SpawnRole}` for them, but
 * openapi-typescript discards `propertyNames` and widens the result to an open
 * `{ [key: string]: T }` index signature. Under that signature `catalog.student`
 * type-checks as a guaranteed `ResourceTierOptions` even when the key is absent,
 * and a typo like `catalog.studnet` type-checks too. Re-narrowing to the
 * generated `SpawnRole` union restores both checks. The union itself still comes
 * from the schema, so adding a spawn role on the backend propagates here.
 */
import type { components } from "./schema";

type Schemas = components["schemas"];

/** A map keyed by spawn role, with every role present. */
export type SpawnRoleMap<T> = Record<SpawnRole, T>;
/** A map keyed by spawn role where roles may be absent (the backend defaults these to `{}`). */
export type PartialSpawnRoleMap<T> = Partial<Record<SpawnRole, T>>;

// ── Selections ───────────────────────────────────────────────────────
export type SpawnRole = Schemas["SpawnRole"];
export type ImageSelection = Schemas["ImageSelection"];
export type SpawnRoleSelection = Schemas["SpawnRoleSelection"];

export type ResourcesSelection = PartialSpawnRoleMap<string>;
export type ProfileSelection = PartialSpawnRoleMap<string>;

// ── Environment ──────────────────────────────────────────────────────
export type Environment = Omit<
  Schemas["Environment"],
  "resources" | "profiles"
> & {
  resources: ResourcesSelection;
  profiles: ProfileSelection;
};

export type EnvironmentUpdate = Omit<
  Schemas["EnvironmentUpdate"],
  "resources" | "profiles"
> & {
  resources?: ResourcesSelection | null;
  profiles?: ProfileSelection | null;
};

// ── Courses ──────────────────────────────────────────────────────────
export type CourseMetadata = Schemas["CourseMetadata"];
export type CourseMetadataUpdate = Schemas["CourseMetadataUpdate"];
export type CourseCapabilities = Schemas["CourseCapabilities"];
export type CourseCollectionCapabilities =
  Schemas["CourseCollectionCapabilities"];

export type CourseConfig = Omit<
  Schemas["CourseConfig"],
  "spawn_role_selections" | "terms"
> & {
  spawn_role_selections: SpawnRoleMap<SpawnRoleSelection>;
  /** Keyed by term id, not by spawn role. */
  terms?: Record<string, TermConfig>;
};

export type CourseSummaryResponse = Schemas["CourseSummaryResponse"];

export type CourseDetailResponse = Omit<
  Schemas["CourseDetailResponse"],
  "environment"
> & {
  environment: Environment;
};

export type CourseCollectionResponse = Schemas["CourseCollectionResponse"];

// ── Terms ────────────────────────────────────────────────────────────
export type TermConfig = Omit<
  Schemas["TermConfig"],
  "spawn_role_selections"
> & {
  spawn_role_selections: SpawnRoleMap<SpawnRoleSelection>;
};

export type TermSummaryCapabilities = Schemas["TermSummaryCapabilities"];
export type TermMembershipCapabilities = Schemas["TermMembershipCapabilities"];
export type TermCapabilities = Schemas["TermCapabilities"];
export type TermSummaryResponse = Schemas["TermSummaryResponse"];

export type TermDetailResponse = Omit<
  Schemas["TermDetailResponse"],
  "environment"
> & {
  environment: Environment;
};

export type CreateTermRequest = Omit<Schemas["CreateTermRequest"], "term"> & {
  term?: TermConfig | null;
};

// ── Membership ───────────────────────────────────────────────────────
export type MembershipCapabilities = Schemas["MembershipCapabilities"];
export type MembershipCollectionResponse =
  Schemas["MembershipCollectionResponse"];
export type MembershipPatch = Schemas["MembershipPatch"];

// ── Infrastructure catalogs ──────────────────────────────────────────
// The backend names these `*Options`; the UI has always called them catalogs.
export type ProfileOption = Schemas["ProfileOption"];
export type ProfileDetails = Schemas["ProfileOptions"];
export type TagInfo = Schemas["ImageTagInfo"];
export type ImageFamily = Schemas["ImageFamilyOption"];
export type ImageCatalog = Schemas["ImageFamilyOptions"];
export type ResourceTier = Schemas["ResourceTierOption"];
export type ResourceTiers = Schemas["ResourceTierOptions"];

export type ResourceCatalog = SpawnRoleMap<ResourceTiers>;
export type ProfileCatalog = SpawnRoleMap<ProfileDetails>;

export type InfrastructureCapabilities = Schemas["InfrastructureCapabilities"];

export type ImageCatalogResponse = Schemas["ImageCatalogResponse"];

export type ResourceCatalogResponse = Omit<
  Schemas["ResourceTiersResponse"],
  "catalog"
> & {
  catalog: ResourceCatalog;
};

export type ProfileCatalogResponse = Omit<
  Schemas["ProfileCatalogResponse"],
  "catalog"
> & {
  catalog: ProfileCatalog;
};

// ── Me ───────────────────────────────────────────────────────────────
export type CurrentUser = Schemas["UserResponse"];
