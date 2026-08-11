import { Card, CardTitle } from "@components/ui/Card";
import { Row } from "@components/ui/Row";
import { useImageCatalog, useResourceCatalog } from "@hooks/catalog";
import { useCourseMetadata, useCourse } from "@hooks/course";

interface Props {
  courseId: string;
}

export function CourseOverviewTab({ courseId }: Props) {
  const { data: course, isLoading } = useCourse(courseId);
  const { data: imageCatalog } = useImageCatalog();
  const { data: resourceCatalog } = useResourceCatalog();
  const { data: courseMetadata } = useCourseMetadata(courseId);

  if (isLoading) return <p className="text-gray-500">Loading…</p>;
  if (!course) return null;

  const termIds = Object.keys(course.terms);

  const imageDisplayName = course.environment.image?.family
    ? (imageCatalog?.catalog.families[course.environment.image.family]
        ?.display_name ?? course.environment.image.family)
    : "—";
  const studentDisplayName = course.environment.resources?.student
    ? (resourceCatalog?.catalog.student.tiers[
        course.environment.resources.student
      ]?.display_name ?? course.environment.resources.student)
    : "—";
  const graderDisplayName = course.environment.resources?.grader
    ? (resourceCatalog?.catalog.grader.tiers[
        course.environment.resources.grader
      ]?.display_name ?? course.environment.resources.grader)
    : "—";

  return (
    <div className="inline-grid grid-cols-1 gap-6">
      <div>
        <Card>
          <CardTitle>Course Information</CardTitle>
          <Row label="Course ID">{courseId}</Row>
          <Row label="Course Name">{courseMetadata?.course_name}</Row>
          <Row label="Description">{courseMetadata?.description}</Row>
          <Row label="Terms">{termIds.length}</Row>
        </Card>
      </div>

      <div>
        <Card>
          <CardTitle>Current Term Template</CardTitle>
          <Row label="Notebook Image">{imageDisplayName}</Row>
          <Row label="Student Resources">{studentDisplayName}</Row>
          <Row label="Grader Resources">{graderDisplayName}</Row>
        </Card>
      </div>
    </div>
  );
}
