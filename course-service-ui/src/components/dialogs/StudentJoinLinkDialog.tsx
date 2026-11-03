import { useState } from "react";
import { Modal } from "@components/ui/Modal";
import { Button } from "@components/ui/Button";
import { Alert } from "@components/ui/Alert";
import { DateTimeField } from "@components/ui/DateTimeField";
import { useUpdateTermStudentJoinLink } from "@hooks/course";
import { getErrorMessage } from "@/lib/errorMessage";
import { fromDateTimeLocal, toDateTimeLocal } from "@/lib/dateTime";

interface Props {
  courseId: string;
  termId: string;
  /** Whether the link is already on; it then keeps its token. */
  isOn: boolean;
  /** The expiry the form starts from, or `null` for none. */
  expiresAt: string | null;
  onClose: () => void;
}

/**
 * Turns a semester's student join link on, or changes when it expires. Mount it
 * only while open, so the form starts from `expiresAt` every time.
 */
export function StudentJoinLinkDialog({
  courseId,
  termId,
  isOn,
  expiresAt,
  onClose,
}: Props) {
  const [expiry, setExpiry] = useState(() => toDateTimeLocal(expiresAt));
  const update = useUpdateTermStudentJoinLink(courseId, termId);

  const handleClose = () => {
    if (update.isPending) return;
    onClose();
  };

  const handleSave = () => {
    update.mutate(
      { expires_at: fromDateTimeLocal(expiry) },
      { onSuccess: onClose },
    );
  };

  const savingLabel = isOn ? "Saving…" : "Turning on…";

  return (
    <Modal
      open
      onClose={handleClose}
      title={isOn ? "Change link expiry" : "Turn on student join link"}
      description="Anyone with the link can join this semester as a student until it expires."
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
            disabled={update.isPending}
          >
            {update.isPending ? savingLabel : isOn ? "Save" : "Turn on"}
          </Button>
        </>
      }
    >
      {update.error && (
        <Alert className="mb-4" title="Could not save the join link">
          {getErrorMessage(update.error)}
        </Alert>
      )}
      <DateTimeField
        label="Expires"
        value={expiry}
        onChange={setExpiry}
        defaultTime="23:55"
        hint="Leave empty to keep the link working until it is turned off."
        disabled={update.isPending}
      />
    </Modal>
  );
}
