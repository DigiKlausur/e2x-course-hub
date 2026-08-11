import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Card, CardTitle } from "@components/ui/Card";
import { Button } from "@components/ui/Button";
import { useCourse } from "@hooks/course";
import { useCreateTerm } from "@hooks/course";
import { CreateTermDialog } from "@components/dialogs/CreateTermDialog";

interface Props {
  courseId: string;
}

export function CourseTermsTab({ courseId }: Props) {
  const navigate = useNavigate();
  const { data: course, isLoading } = useCourse(courseId);
  const createTerm = useCreateTerm(courseId);
  const [dialogOpen, setDialogOpen] = useState(false);

  if (isLoading) return <p className="text-gray-500">Loading…</p>;

  const termIds = course ? course.terms.map((term) => term.term_id) : [];

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
        <div className="flex justify-between items-center mb-5">
          <CardTitle>Semesters</CardTitle>
          <Button variant="primary" onClick={() => setDialogOpen(true)}>
            + Create Semester
          </Button>
        </div>

        {termIds.length === 0 && (
          <p className="text-gray-400 text-sm">No semesters yet.</p>
        )}

        {termIds.map((termId) => (
          <div
            key={termId}
            className="flex justify-between items-center py-4 border-b border-gray-100 last:border-b-0"
          >
            <div>
              <Link
                to={`/course/${courseId}/term/${termId}`}
                className="font-semibold text-hbrs-dark-blue hover:text-hbrs-medium-blue hover:underline"
              >
                {termId}
              </Link>
            </div>
          </div>
        ))}
      </Card>
    </div>
  );
}
