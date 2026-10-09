import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Card, CardTitle } from "@components/ui/Card";
import { Row } from "@components/ui/Row";
import { Button } from "@components/ui/Button";
import { Alert } from "@components/ui/Alert";
import { DataTable } from "@components/ui/DataTable";
import type { DataTableColumn } from "@components/ui/DataTable";
import { CreateTermDialog } from "@components/dialogs/CreateTermDialog";
import { RuntimeConfigEditor } from "@components/infrastructure/RuntimeConfigEditor";
import { useImageCatalog, useResourceCatalog } from "@hooks/catalog";
import {
  useCourseMetadata,
  useCourse,
  useCreateTerm,
  useUpdateCourseEnvironment,
} from "@hooks/course";
import { getErrorMessage } from "@/lib/errorMessage";
import { courseActionText } from "@domain/actions";
import type {
  ImageSelection,
  SpawnRole,
  TermSummaryResponse,
} from "@api/types";

interface Props {
  courseId: string;
}

function buildSemesterColumns(
  courseId: string,
): DataTableColumn<TermSummaryResponse>[] {
  return [
    {
      id: "term_id",
      header: "Semester",
      cell: (term) =>
        term.actions.view ? (
          <Link
            to={`/course/${courseId}/term/${term.term_id}`}
            className="font-semibold text-hbrs-dark-blue hover:text-hbrs-medium-blue hover:underline"
          >
            {term.term_id}
          </Link>
        ) : (
          // Opening a term requires TERM_VIEW; without it the page would only
          // 403, so show the id as plain text instead of a dead link.
          <span className="font-semibold text-gray-400">{term.term_id}</span>
        ),
      sortAccessor: (term) => term.term_id.toLowerCase(),
    },
  ];
}

function matchesTermQuery(term: TermSummaryResponse, query: string): boolean {
  return term.term_id.toLowerCase().includes(query);
}

export function CourseOverviewTab({ courseId }: Props) {
  const navigate = useNavigate();
  const { data: course, isLoading } = useCourse(courseId);
  const { data: imageCatalog } = useImageCatalog();
  const { data: resourceCatalog } = useResourceCatalog();
  const { data: courseMetadata } = useCourseMetadata(courseId);
  const createTerm = useCreateTerm(courseId);
  const updateEnvironment = useUpdateCourseEnvironment(courseId);
  const [dialogOpen, setDialogOpen] = useState(false);

  if (isLoading) return <p className="text-gray-500">Loading…</p>;
  if (!course) return null;

  const terms = course.terms;
  const termIds = terms.map((term) => term.term_id);
  const canAddTerm = course.actions.terms.add;
  const semesterColumns = buildSemesterColumns(courseId);

  const handleCreate = async (termId: string) => {
    await createTerm.mutateAsync({ termId, termConfig: {} });
    navigate(`/course/${courseId}/term/${termId}`);
  };

  const handleImageConfirm = (selection: ImageSelection) => {
    updateEnvironment.mutate({ image: selection });
  };

  const handleResourceConfirm = (role: SpawnRole, tier: string) => {
    updateEnvironment.mutate({ resources: { [role]: tier } });
  };

  return (
    <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-[2fr_1fr]">
      <div>
        <Card>
          <CreateTermDialog
            open={dialogOpen}
            onClose={() => setDialogOpen(false)}
            existingTermIds={termIds}
            onCreate={handleCreate}
            isSubmitting={createTerm.isPending}
          />

          {createTerm.error && (
            <Alert className="mb-4" title="Could not create the semester">
              {getErrorMessage(createTerm.error)}
            </Alert>
          )}

          <CardTitle>Semesters</CardTitle>

          <DataTable
            rows={terms}
            getRowId={(term) => term.term_id}
            columns={semesterColumns}
            pageSizeStorageKey="course-semesters-table-page-size"
            defaultSort={{ columnId: "term_id", direction: "asc" }}
            emptyMessage="No semesters yet."
            noMatchMessage="No matching semesters."
            filter={{
              placeholder: "Filter semesters...",
              predicate: matchesTermQuery,
            }}
            toolbarEnd={
              canAddTerm && (
                <Button
                  variant="primary"
                  onClick={() => setDialogOpen(true)}
                  title={courseActionText.terms.add.description}
                >
                  + {courseActionText.terms.add.label}
                </Button>
              )
            }
          />
        </Card>
      </div>

      <div>
        <Card>
          <CardTitle>Course Information</CardTitle>
          <Row label="Course ID">{courseId}</Row>
          <Row label="Course Name">{courseMetadata?.course_name}</Row>
          <Row label="Description">{courseMetadata?.description}</Row>
        </Card>

        <RuntimeConfigEditor
          title="Current Semester Template"
          description={courseActionText.environment.select.description}
          imageSelection={course.environment.image}
          resourcesSelection={course.environment.resources}
          imageCatalog={imageCatalog?.catalog}
          resourceCatalog={resourceCatalog?.catalog}
          canEdit={course.actions.environment.select}
          showTag={false}
          errorMessage={
            updateEnvironment.error
              ? getErrorMessage(updateEnvironment.error)
              : undefined
          }
          onImageConfirm={handleImageConfirm}
          onResourceConfirm={handleResourceConfirm}
        />
      </div>
    </div>
  );
}
