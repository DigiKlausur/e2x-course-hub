export interface ImageSelection {
  family: string;
  tag?: string;
}

export interface ResourcesSelection {
  student?: string;
  grader?: string;
}

export interface ProfileSelection {
  student?: string;
  grader?: string;
}

export interface Environment {
  image: ImageSelection;
  resources: ResourcesSelection;
}

export interface EnvironmentUpdate {
  image?: ImageSelection;
  resources?: ResourcesSelection;
}

export interface TermConfig {
  image?: ImageSelection;
  resources?: ResourcesSelection;
  profiles?: ProfileSelection;
}

export interface TermSummaryCapabilities {
  viewTerm: boolean;
  removeTerm: boolean;
}

export interface TermCapabilities extends TermSummaryCapabilities {
  viewInstructors: boolean;
  manageInstructors: boolean;
  viewTeachingAssistants: boolean;
  manageTeachingAssistants: boolean;
  viewStudents: boolean;
  manageStudents: boolean;
  viewObservers: boolean;
  manageObservers: boolean;
  selectEnvironment: boolean;
}

export interface TermSummaryResponse {
  course_id: string;
  term_id: string;
  capabilities: TermSummaryCapabilities;
}

export interface TermDetailResponse {
  course_id: string;
  term_id: string;
  environment: Environment;
  capabilities: TermCapabilities;
}

export interface CreateTermRequest {
  /** Request body for creating a term. */
  term?: TermConfig | null;
}

export interface MembershipCollectionResponse {
  usernames: string[];
  capabilities: {
    manage: boolean;
    view: boolean;
  };
}

export interface MembershipPatch {
  /** Usernames to add. */
  add?: string[];
  /** Usernames to remove. */
  remove?: string[];
}

export interface CourseMetadata {
  course_id: string;
  course_name: string;
  description?: string;
}

export interface CourseMetadataUpdate {
  course_name?: string | null;
  description?: string | null;
}

export interface CourseConfig {
  metadata: CourseMetadata;
  image: ImageSelection;
  resources: ResourcesSelection;
  profiles: ProfileSelection;
  terms: Record<string, TermConfig>;
}

export interface CourseCapabilities {
  editMetadata: boolean;
  removeCourse: boolean;
  selectEnvironment: boolean;
  viewCourseOwners: boolean;
  manageCourseOwners: boolean;
  addTerm: boolean;
}

export interface CourseSummaryResponse {
  metadata: CourseMetadata;
  capabilities: CourseCapabilities;
}

export interface CourseDetailResponse {
  metadata: CourseMetadata;
  environment: Environment;
  terms: TermSummaryResponse[];
  capabilities: CourseCapabilities;
}

export interface CourseCollectionResponse {
  courses: CourseSummaryResponse[];
  capabilities: {
    createCourse: boolean;
  };
}

export interface BaseProfile {
  name: string;
  display_name: string;
  environment: Record<string, string | number | boolean>;
  mounts: string[];
}

export interface ProfileDetails {
  default: string;
  profiles: BaseProfile[];
}

export interface Image {
  name: string;
  tag: string;
  pullPolicy: string;
}

export interface Resources {
  cpu_guarantee: string;
  cpu_limit: string;
  mem_guarantee: string;
  mem_limit: string;
}

export interface Runtime {
  image: Image;
  resources: Resources;
  environment: Record<string, string>;
}

export interface TagInfo {
  status: "active" | "deprecated" | "removed";
  message?: string;
}

export interface ImageFlavors {
  student: string;
  grader: string;
}

export interface ImageFamily {
  display_name: string;
  description: string;
  default_tag: string;
  pullPolicy?: string;
  registry?: string;
  images: ImageFlavors;
  tags: Record<string, TagInfo>;
}

export interface ImageCatalog {
  default_registry: string;
  default_pull_policy?: string;
  default_family: string;
  families: Record<string, ImageFamily>;
}

export interface ResourceTier {
  display_name: string;
  description: string;
  resources: Resources;
  warning?: string;
}

export interface ResourceTiers {
  default_tier: string;
  tiers: Record<string, ResourceTier>;
}

export interface ResourceCatalog {
  student: ResourceTiers;
  grader: ResourceTiers;
}

export interface InfrastructureCapabilities {
  manage: boolean;
  view: boolean;
}

export interface ImageCatalogResponse {
  capabilities: InfrastructureCapabilities;
  catalog: ImageCatalog;
}

export interface ResourceCatalogResponse {
  capabilities: InfrastructureCapabilities;
  catalog: ResourceCatalog;
}

export interface Profiles {
  default: string;
  profiles: string[];
}

export interface ProfileCatalog {
  student: ProfileDetails;
  grader: ProfileDetails;
}

export interface ProfileCatalogResponse {
  capabilities: InfrastructureCapabilities;
  catalog: ProfileCatalog;
}

export interface CurrentUser {
  username: string;
}
