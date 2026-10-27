import { useState } from "react";
import { Modal } from "@components/ui/Modal";
import { Button } from "@components/ui/Button";
import { Alert } from "@components/ui/Alert";
import { StudentAccessPeriodFields } from "@components/term/StudentAccessPeriodFields";
import { useUpdateTermAccessPeriod } from "@hooks/course";
import { getErrorMessage } from "@/lib/errorMessage";
import { termActionText } from "@domain/actions";
import {
  accessPeriodDraftError,
  fromAccessPeriodDraft,
  toAccessPeriodDraft,
} from "@domain/accessPeriod";
import type { StudentAccessPeriod } from "@api/types";

interface Props {
  courseId: string;
  termId: string;
  accessPeriod: StudentAccessPeriod;
  onClose: () => void;
}

/**
 * Edits a semester's student access period. Mount it only while open, so the
 * form starts from the current period every time.
 */
export function StudentAccessPeriodDialog({
  courseId,
  termId,
  accessPeriod,
  onClose,
}: Props) {
  const [draft, setDraft] = useState(() => toAccessPeriodDraft(accessPeriod));
  const update = useUpdateTermAccessPeriod(courseId, termId);

  const handleClose = () => {
    if (update.isPending) return;
    onClose();
  };

  const handleSave = () => {
    update.mutate(fromAccessPeriodDraft(draft), { onSuccess: onClose });
  };

  return (
    <Modal
      open
      onClose={handleClose}
      title={termActionText.accessPeriod.edit.label}
      description={termActionText.accessPeriod.edit.description}
      footer={
        <>
          <Button
            variant="secondary"
            onClick={handleClose}
            disabled={update.isPending}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSave}
            disabled={
              update.isPending || accessPeriodDraftError(draft) !== null
            }
          >
            {update.isPending ? "Saving…" : "Save"}
          </Button>
        </>
      }
    >
      {update.error && (
        <Alert className="mb-4" title="Could not save the access period">
          {getErrorMessage(update.error)}
        </Alert>
      )}
      <StudentAccessPeriodFields
        value={draft}
        onChange={setDraft}
        disabled={update.isPending}
      />
    </Modal>
  );
}
