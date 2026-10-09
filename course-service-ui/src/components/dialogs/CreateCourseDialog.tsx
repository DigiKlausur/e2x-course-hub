import { useMemo, useState } from "react";
import { Modal } from "@components/ui/Modal";
import { Button } from "@components/ui/Button";

interface Props {
  open: boolean;
  onClose: () => void;
  existingCourseIds: string[];
  onCreate: (data: {
    courseId: string;
    courseName: string;
    description: string;
  }) => Promise<void>;
  isSubmitting: boolean;
}

export function CreateCourseDialog({
  open,
  onClose,
  existingCourseIds,
  onCreate,
  isSubmitting,
}: Props) {
  const [courseId, setCourseId] = useState("");
  const [courseName, setCourseName] = useState("");
  const [description, setDescription] = useState("");

  const normalizedExistingIds = useMemo(
    () => new Set(existingCourseIds.map((id) => id.trim().toLowerCase())),
    [existingCourseIds],
  );

  const isDuplicate =
    courseId.trim().length > 0 &&
    normalizedExistingIds.has(courseId.trim().toLowerCase());
  const isValidId = /^[A-Za-z0-9][A-Za-z0-9-_]+$/.test(courseId.trim());
  const isValid = isValidId && courseName.trim().length > 0 && !isDuplicate;

  const handleClose = () => {
    if (isSubmitting) return;
    setCourseId("");
    setCourseName("");
    setDescription("");
    onClose();
  };

  const handleSubmit = async () => {
    if (!isValid) return;
    await onCreate({
      courseId: courseId.trim(),
      courseName: courseName.trim(),
      description: description.trim(),
    });
    handleClose();
  };

  const fieldClass =
    "w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-hbrs-dark-blue";

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title="Create Course"
      description="Provide basic course metadata. Default image and resources will be taken from the infrastructure catalogs."
      footer={
        <>
          <Button
            variant="secondary"
            onClick={handleClose}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={!isValid || isSubmitting}
          >
            {isSubmitting ? "Creating…" : "Create Course"}
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-4">
        <div>
          <label className="block text-sm font-semibold mb-1.5">
            Course ID
          </label>
          <input
            value={courseId}
            onChange={(e) => setCourseId(e.target.value)}
            placeholder="e.g. math101"
            autoFocus
            className={fieldClass}
          />
          {courseId.trim().length > 0 && !isValidId && (
            <p className="text-xs text-red-600 mt-1">
              Use at least 2 characters: letters, numbers, dashes, or
              underscores.
            </p>
          )}
          {isDuplicate && (
            <p className="text-xs text-red-600 mt-1">
              A course with this ID already exists.
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-semibold mb-1.5">
            Course Name
          </label>
          <input
            value={courseName}
            onChange={(e) => setCourseName(e.target.value)}
            placeholder="e.g. Mathematics 101"
            className={fieldClass}
          />
        </div>

        <div>
          <label className="block text-sm font-semibold mb-1.5">
            Description{" "}
            <span className="font-normal text-gray-400">(optional)</span>
          </label>
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Short description"
            className={fieldClass}
          />
        </div>
      </div>
    </Modal>
  );
}
