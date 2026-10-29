import { useMemo, useState } from "react";
import { Modal } from "@components/ui/Modal";
import { Button } from "@components/ui/Button";
import { Alert } from "@components/ui/Alert";
import { StudentAccessPeriodFields } from "@components/term/StudentAccessPeriodFields";
import { getErrorMessage } from "@/lib/errorMessage";
import { semesterTemplateTitle } from "@domain/actions";
import { describeUnavailable, isChangeableInUi } from "@domain/unavailable";
import type { ApiError } from "@api/client";
import type { SpawnRole, UnavailableSelection } from "@api/types";
import {
  accessPeriodDraftError,
  fromAccessPeriodDraft,
  undecidedAccessPeriodDraft,
} from "@domain/accessPeriod";
import type { StudentAccessPeriod } from "@api/types";

interface Props {
  open: boolean;
  onClose: () => void;
  existingTermIds: string[];
  /** `accessPeriod` is `null` when student access is not restricted. */
  onCreate: (
    termId: string,
    accessPeriod: StudentAccessPeriod | null,
  ) => Promise<void>;
  isSubmitting: boolean;
  /** The error of the last failed create, shown at the top of the dialog. */
  error?: unknown;
}

/** The kind of selection and the `extra` key of its name, per not-found error type. */
const UNAVAILABLE_ERRORS = {
  "urn:e2x-course-hub:image-family-not-found": ["image_family", "family_name"],
  "urn:e2x-course-hub:resource-tier-not-found": ["resource_tier", "tier_name"],
  "urn:e2x-course-hub:profile-not-found": ["profile", "profile_name"],
} as const;

/** The template selection a failed create names as missing from the catalog, if any. */
function unavailableFromError(error: unknown): UnavailableSelection | null {
  const response = (error as ApiError).response;
  const entry =
    UNAVAILABLE_ERRORS[response?.type as keyof typeof UNAVAILABLE_ERRORS];
  if (!entry) return null;
  const [kind, nameKey] = entry;
  const extra = response?.extra ?? {};
  return {
    kind,
    name: String(extra[nameKey]),
    spawn_role: extra.spawn_role as SpawnRole | undefined,
  };
}

/** The error of a failed create; a selection the catalog no longer has gets a message saying what to do. */
function CreateTermErrorAlert({ error }: { error: unknown }) {
  const item = unavailableFromError(error);
  return (
    <Alert className="mb-4" title="Could not create the semester">
      {item ? (
        <>
          {describeUnavailable(item)}
          {isChangeableInUi(item) && (
            <>
              {" "}
              Select a new one under <strong>{semesterTemplateTitle}</strong>,
              then try again.
            </>
          )}
        </>
      ) : (
        getErrorMessage(error)
      )}
    </Alert>
  );
}

export function CreateTermDialog({
  open,
  onClose,
  existingTermIds,
  onCreate,
  isSubmitting,
  error,
}: Props) {
  const [termId, setTermId] = useState("");
  const [accessPeriod, setAccessPeriod] = useState(undecidedAccessPeriodDraft);

  const normalizedExisting = useMemo(
    () => new Set(existingTermIds.map((id) => id.trim().toLowerCase())),
    [existingTermIds],
  );

  const isDuplicate =
    termId.trim().length > 0 &&
    normalizedExisting.has(termId.trim().toLowerCase());
  const isValidId = /^[A-Za-z0-9][A-Za-z0-9-_]+$/.test(termId.trim());
  const isValid =
    isValidId && !isDuplicate && accessPeriodDraftError(accessPeriod) === null;

  const handleClose = () => {
    if (isSubmitting) return;
    setTermId("");
    setAccessPeriod(undecidedAccessPeriodDraft);
    onClose();
  };

  const handleSubmit = async () => {
    if (!isValid) return;
    try {
      await onCreate(
        termId.trim(),
        accessPeriod.restricted ? fromAccessPeriodDraft(accessPeriod) : null,
      );
    } catch {
      return; // Stay open; the error is shown through the `error` prop.
    }
    handleClose();
  };

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title="Create Semester"
      description="The new semester will inherit the course's current runtime template settings."
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
            {isSubmitting ? "Creating…" : "Create Semester"}
          </Button>
        </>
      }
    >
      {error ? <CreateTermErrorAlert error={error} /> : null}

      <div>
        <label className="block text-sm font-semibold mb-1.5">
          Semester ID
        </label>
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
            A semester with this ID already exists.
          </p>
        )}
      </div>

      <div className="mt-5">
        <StudentAccessPeriodFields
          value={accessPeriod}
          onChange={setAccessPeriod}
          disabled={isSubmitting}
        />
      </div>
    </Modal>
  );
}
