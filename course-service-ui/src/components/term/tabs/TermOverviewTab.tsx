import { Card, CardTitle } from "@components/ui/Card";
import { Row } from "@components/ui/Row";
import { Badge } from "@components/ui/Badge";
import { useTermEnvironment } from "@hooks/course";
import { useImageCatalog, useResourceCatalog } from "@hooks/catalog";

interface Props {
  courseId: string;
  termId: string;
}

export function TermOverviewTab({ courseId, termId }: Props) {
  const { data: termEnvironment, isLoading } = useTermEnvironment(
    courseId,
    termId,
  );
  const { data: imageCatalog } = useImageCatalog();
  const { data: resourceCatalog } = useResourceCatalog();

  if (isLoading) return <p className="text-gray-500">Loading…</p>;

  const imageDisplayName = termEnvironment?.image?.family
    ? (imageCatalog?.catalog.families[termEnvironment.image.family]
        ?.display_name ?? termEnvironment.image.family)
    : "—";
  const studentDisplayName = termEnvironment?.resources?.student
    ? (resourceCatalog?.catalog.student.tiers[termEnvironment.resources.student]
        ?.display_name ?? termEnvironment.resources.student)
    : "—";
  const graderDisplayName = termEnvironment?.resources?.grader
    ? (resourceCatalog?.catalog.grader.tiers[termEnvironment.resources.grader]
        ?.display_name ?? termEnvironment.resources.grader)
    : "—";

  return (
    <div className="grid grid-cols-[2fr_1fr] gap-6">
      <div>
        <Card>
          <CardTitle>General Information</CardTitle>
          <Row label="Course">{courseId}</Row>
          <Row label="Term">{termId}</Row>
        </Card>
      </div>

      <div>
        <Card>
          <CardTitle>Configuration Summary</CardTitle>
          <Row label="Status">
            <Badge variant="active">Active</Badge>
          </Row>
          <Row label="Notebook Image">{imageDisplayName}</Row>
          <Row label="Student Resources">{studentDisplayName}</Row>
          <Row label="Grader Resources">{graderDisplayName}</Row>
        </Card>
      </div>
    </div>
  );
}
