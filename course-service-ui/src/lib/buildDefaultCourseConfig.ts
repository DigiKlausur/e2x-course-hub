import type {
  CourseConfig,
  ImageCatalog,
  ProfileCatalog,
  ResourceCatalog,
} from "@api/types";

interface BuildDefaultCourseConfigParams {
  courseId: string;
  courseName: string;
  description: string;
  imageCatalog?: ImageCatalog;
  resourceCatalog?: ResourceCatalog;
  profileCatalog?: ProfileCatalog;
}

export function buildDefaultCourseConfig({
  courseId,
  courseName,
  description,
  imageCatalog,
  resourceCatalog,
  profileCatalog,
}: BuildDefaultCourseConfigParams): CourseConfig | null {
  if (!imageCatalog || !resourceCatalog || !profileCatalog) {
    return null;
  }

  const fallbackImageFamily = Object.keys(imageCatalog.families)[0];
  const selectedImageFamily =
    imageCatalog.default_family || fallbackImageFamily;
  const selectedFamily = imageCatalog.families[selectedImageFamily];
  if (!selectedFamily) return null;

  const fallbackTag = Object.keys(selectedFamily.tags)[0];

  return {
    metadata: {
      course_id: courseId,
      course_name: courseName,
      description: description || undefined,
    },
    image: {
      family: selectedImageFamily,
      tag: selectedFamily.default_tag || fallbackTag,
    },
    spawn_role_selections: {
      student: {
        resource_tier_name: resourceCatalog.student.default_tier,
        profile_name: profileCatalog.student.default_profile,
      },
      grader: {
        resource_tier_name: resourceCatalog.grader.default_tier,
        profile_name: profileCatalog.grader.default_profile,
      },
    },
    terms: {},
  };
}
