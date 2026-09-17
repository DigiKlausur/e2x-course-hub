import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Card, CardTitle } from "@components/ui/Card";
import { Button } from "@components/ui/Button";
import { useCourse } from "@hooks/course";
import { useCreateTerm } from "@hooks/course";
import { CreateTermDialog } from "@components/dialogs/CreateTermDialog";
import { Alert } from "@components/ui/Alert";
import { getErrorMessage } from "@/lib/errorMessage";

interface Props {
  courseId: string;
}

export function CourseTermsTab({ courseId }: Props) {
  const navigate = useNavigate();
  const { data: course, isLoading } = useCourse(courseId);
  const createTerm = useCreateTerm(courseId);
  const [dialogOpen, setDialogOpen] = useState(false);

  if (isLoading) return <p className="text-gray-500">Loading…</p>;

  const terms = course?.terms ?? [];
  const termIds = terms.map((term) => term.term_id);
  const canAddTerm = course?.capabilities.addTerm ?? false;

  const handleCreate = async (termId: string) => {
    await createTerm.mutateAsync({ termId, termConfig: {} });
    navigate(`/course/${courseId}/term/${termId}`);
  };

  return (
    <div className="max-w-2xl">
      <CreateTermDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        existingTermIds={termIds}
        onCreate={handleCreate}
        isSubmitting={createTerm.isPending}
      />
      <Card>
        {createTerm.error && (
          <Alert className="mb-4" title="Could not create the semester">
            {getErrorMessage(createTerm.error)}
          </Alert>
        )}

        <div className="flex justify-between items-center mb-5">
          <CardTitle>Semesters</CardTitle>
          {canAddTerm && (
            <Button variant="primary" onClick={() => setDialogOpen(true)}>
              + Create Semester
            </Button>
          )}
        </div>

        {terms.length === 0 && (
          <p className="text-gray-400 text-sm">No semesters yet.</p>
        )}

        {terms.map((term) => (
          <div
            key={term.term_id}
            className="flex justify-between items-center py-4 border-b border-gray-100 last:border-b-0"
          >
            <div>
              {/* Opening a term requires TERM_VIEW; without it the page would
                  only 403, so show the id as plain text instead of a dead link. */}
              {term.capabilities.viewTerm ? (
                <Link
                  to={`/course/${courseId}/term/${term.term_id}`}
                  className="font-semibold text-hbrs-dark-blue hover:text-hbrs-medium-blue hover:underline"
                >
                  {term.term_id}
                </Link>
              ) : (
                <span className="font-semibold text-gray-400">
                  {term.term_id}
                </span>
              )}
            </div>
          </div>
        ))}
      </Card>
    </div>
  );
}
