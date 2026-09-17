import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardTitle } from "@components/ui/Card";
import { Row } from "@components/ui/Row";
import { Button } from "@components/ui/Button";
import { Alert } from "@components/ui/Alert";
import { ConfirmDialog } from "@components/ui/ConfirmDialog";
import { useDeleteTerm, useTerm } from "@hooks/course";
import { getErrorMessage } from "@/lib/errorMessage";

interface Props {
  courseId: string;
  termId: string;
}

export function TermSettingsTab({ courseId, termId }: Props) {
  const navigate = useNavigate();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  const { data: term, isLoading } = useTerm(courseId, termId);
  const deleteTerm = useDeleteTerm(courseId, termId);

  const canRemoveTerm = term?.capabilities.removeTerm ?? false;

  // Term ids repeat across courses, so the course id has to be part of the
  // confirmation for it to name one specific term.
  const confirmationText = `${courseId}-${termId}`;

  if (isLoading) return <p className="text-gray-500">Loading…</p>;

  return (
    <div className="grid grid-cols-[2fr_1fr] gap-6">
      <div>
        {/* Terms have no editable metadata: they are identified by their id and
            carry only an environment. Runtime settings live in the Term Runtime
            tab, so this card is read-only. */}
        <Card>
          <CardTitle>Term Settings</CardTitle>
          <Row label="Course">{courseId}</Row>
          <Row label="Term">{termId}</Row>
        </Card>
      </div>

      <div>
        {canRemoveTerm && (
          <Card>
            <CardTitle>Danger Zone</CardTitle>
            <p className="text-sm text-gray-500 mb-4">
              Permanently remove this term.
            </p>

            {deleteTerm.error && (
              <Alert className="mb-4" title="Could not delete the term">
                {getErrorMessage(deleteTerm.error)}
              </Alert>
            )}

            <div className="flex flex-col gap-2">
              <Button
                variant="danger"
                onClick={() => setDeleteDialogOpen(true)}
                disabled={deleteTerm.isPending}
              >
                {deleteTerm.isPending ? "Deleting…" : "Delete Term"}
              </Button>
            </div>

            <ConfirmDialog
              open={deleteDialogOpen}
              onClose={() => setDeleteDialogOpen(false)}
              title="Delete term"
              message={`This permanently deletes the term ${termId} of ${courseId}, including its memberships. This cannot be undone.`}
              confirmText="Delete Term"
              variant="destructive"
              requireConfirmationText={confirmationText}
              isConfirming={deleteTerm.isPending}
              onConfirm={() =>
                deleteTerm.mutate(undefined, {
                  onSuccess: () => {
                    setDeleteDialogOpen(false);
                    navigate(`/course/${courseId}`);
                  },
                  onError: () => setDeleteDialogOpen(false),
                })
              }
            />
          </Card>
        )}
      </div>
    </div>
  );
}
