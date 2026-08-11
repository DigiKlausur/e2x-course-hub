import { useMemo, useState } from "react";
import { Modal } from "@components/ui/Modal";
import { Button } from "@components/ui/Button";

interface Props {
  open: boolean;
  onClose: () => void;
  existingTermIds: string[];
  onCreate: (termId: string) => Promise<void>;
  isSubmitting: boolean;
}

export function CreateTermDialog({
  open,
  onClose,
  existingTermIds,
  onCreate,
  isSubmitting,
}: Props) {
  const [termId, setTermId] = useState("");

  const normalizedExisting = useMemo(
    () => new Set(existingTermIds.map((id) => id.trim().toLowerCase())),
    [existingTermIds],
  );

  const isDuplicate =
    termId.trim().length > 0 &&
    normalizedExisting.has(termId.trim().toLowerCase());
  const isValidId = /^[A-Za-z0-9][A-Za-z0-9-_]+$/.test(termId.trim());
  const isValid = isValidId && !isDuplicate;

  const handleClose = () => {
    if (isSubmitting) return;
    setTermId("");
    onClose();
  };

  const handleSubmit = async () => {
    if (!isValid) return;
    await onCreate(termId.trim());
    handleClose();
  };

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title="Create Term"
      description="The new term will inherit the course's current runtime template settings."
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
            {isSubmitting ? "Creating…" : "Create Term"}
          </Button>
        </>
      }
    >
      <div>
        <label className="block text-sm font-semibold mb-1.5">Term ID</label>
        <input
          value={termId}
          onChange={(e) => setTermId(e.target.value)}
          placeholder="e.g. fall-2026"
          autoFocus
          className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-hbrs-dark-blue"
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
        />
        {termId.trim().length > 0 && !isValidId && (
          <p className="text-xs text-red-600 mt-1">
            Use at least 2 characters: letters, numbers, dashes, or underscores.
          </p>
        )}
        {isDuplicate && (
          <p className="text-xs text-red-600 mt-1">
            A term with this ID already exists.
          </p>
        )}
      </div>
    </Modal>
  );
}
