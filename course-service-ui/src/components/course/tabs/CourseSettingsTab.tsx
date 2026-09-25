import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardTitle } from "@components/ui/Card";
import { Button } from "@components/ui/Button";
import { Alert } from "@components/ui/Alert";
import { ConfirmDialog } from "@components/ui/ConfirmDialog";
import {
  useCourse,
  useDeleteCourse,
  useUpdateCourseMetadata,
} from "@hooks/course";
import { getErrorMessage } from "@/lib/errorMessage";
import { courseActionText } from "@domain/actions";

interface Props {
  courseId: string;
}

export function CourseSettingsTab({ courseId }: Props) {
  const navigate = useNavigate();
  const { data: course, isLoading } = useCourse(courseId);
  const metadata = course?.metadata;
  const updateMetadata = useUpdateCourseMetadata(courseId);
  const deleteCourse = useDeleteCourse(courseId);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  // `null` means "untouched, follow the server value". An empty string is a
  // real edit, so these must not collapse to a falsy check — otherwise clearing
  // a field snaps it straight back to the fetched value.
  const [name, setName] = useState<string | null>(null);
  const [description, setDescription] = useState<string | null>(null);

  const currentName = name ?? metadata?.course_name ?? "";
  const currentDescription = description ?? metadata?.description ?? "";

  const canEditMetadata = course?.actions.metadata.edit ?? false;
  const canRemoveCourse = course?.actions.remove ?? false;

  const handleSave = () => {
    updateMetadata.mutate(
      { course_name: currentName, description: currentDescription },
      // Drop the local edits so the form follows the server again, which also
      // makes a rejected save visibly revert instead of looking applied.
      {
        onSuccess: () => {
          setName(null);
          setDescription(null);
        },
      },
    );
  };

  if (isLoading) return <p className="text-gray-500">Loading…</p>;

  if (!canEditMetadata && !canRemoveCourse) {
    return (
      <p className="text-gray-500">
        You are not allowed to change the settings of this course.
      </p>
    );
  }

  const isDirty = name !== null || description !== null;
  const fieldClass =
    "w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-hbrs-dark-blue disabled:bg-gray-50 disabled:text-gray-500";

  return (
    <div className="grid grid-cols-[2fr_1fr] gap-6">
      <div>
        {canEditMetadata && (
          <Card>
            <CardTitle>Course Settings</CardTitle>
            <p className="text-sm text-gray-500 mb-4">
              {courseActionText.metadata.edit.description}
            </p>

            {updateMetadata.error && (
              <Alert className="mb-5" title="Could not save the changes">
                {getErrorMessage(updateMetadata.error)}
              </Alert>
            )}

            <div className="mb-5">
              <label className="block text-sm font-semibold mb-2">
                Course Name
              </label>
              <input
                value={currentName}
                onChange={(e) => setName(e.target.value)}
                disabled={updateMetadata.isPending}
                className={fieldClass}
              />
              {currentName.trim().length === 0 && (
                <p className="text-xs text-red-600 mt-1">
                  A course name is required.
                </p>
              )}
            </div>

            <div className="mb-5">
              <label className="block text-sm font-semibold mb-2">
                Description
              </label>
              <input
                value={currentDescription}
                onChange={(e) => setDescription(e.target.value)}
                disabled={updateMetadata.isPending}
                className={fieldClass}
              />
            </div>

            <Button
              variant="primary"
              onClick={handleSave}
              disabled={
                updateMetadata.isPending ||
                !isDirty ||
                currentName.trim().length === 0
              }
            >
              {updateMetadata.isPending ? "Saving…" : "Save Changes"}
            </Button>
          </Card>
        )}
      </div>

      <div>
        {canRemoveCourse && (
          <Card>
            <CardTitle>Danger Zone</CardTitle>
            <p className="text-sm text-gray-500 mb-4">
              {courseActionText.remove.description}
            </p>

            {deleteCourse.error && (
              <Alert className="mb-4" title="Could not delete the course">
                {getErrorMessage(deleteCourse.error)}
              </Alert>
            )}

            <Button
              variant="danger"
              onClick={() => setDeleteDialogOpen(true)}
              disabled={deleteCourse.isPending}
            >
              {deleteCourse.isPending
                ? "Deleting…"
                : courseActionText.remove.label}
            </Button>

            <ConfirmDialog
              open={deleteDialogOpen}
              onClose={() => setDeleteDialogOpen(false)}
              title="Delete course"
              message={`This permanently deletes ${courseId} and all of its terms, including their memberships. This cannot be undone.`}
              confirmText="Delete Course"
              variant="destructive"
              // Course ids are unique hub-wide, so the id alone identifies
              // exactly what is being destroyed.
              requireConfirmationText={courseId}
              isConfirming={deleteCourse.isPending}
              onConfirm={() =>
                deleteCourse.mutate(undefined, {
                  onSuccess: () => {
                    setDeleteDialogOpen(false);
                    navigate("/");
                  },
                  // Keep the dialog open on failure so the message in the card
                  // behind it is not the only feedback.
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
