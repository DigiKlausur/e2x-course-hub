import { useEffect, useState } from "react";
import { Check, Copy } from "lucide-react";
import { Card, CardTitle } from "@components/ui/Card";
import { Button } from "@components/ui/Button";
import { Alert } from "@components/ui/Alert";
import { ConfirmDialog } from "@components/ui/ConfirmDialog";
import { StudentJoinLinkDialog } from "@components/dialogs/StudentJoinLinkDialog";
import {
  useDeleteTermStudentJoinLink,
  useRegenerateTermStudentJoinLink,
  useTermStudentJoinLink,
} from "@hooks/course";
import { getErrorMessage } from "@/lib/errorMessage";
import { studentJoinLinkUrl } from "@/lib/studentJoinLinkUrl";
import {
  describeStudentJoinLinkExpiry,
  isStudentJoinLinkExpired,
} from "@domain/studentJoinLink";
import { termActionText } from "@domain/actions";

type CopyState = "idle" | "copied" | "failed";

interface Props {
  courseId: string;
  termId: string;
  /** The end of the student access period; a link being turned on expires then by default. */
  accessEnd: string | null;
}

/** Turn on, copy, regenerate and turn off a semester's student join link. Render it only for users who may manage the link. */
export function StudentJoinLinkCard({ courseId, termId, accessEnd }: Props) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [confirm, setConfirm] = useState<"regenerate" | "turn-off" | null>(
    null,
  );
  const [copyState, setCopyState] = useState<CopyState>("idle");

  const {
    data: link,
    isLoading,
    error,
  } = useTermStudentJoinLink(courseId, termId, true);
  const regenerate = useRegenerateTermStudentJoinLink(courseId, termId);
  const turnOff = useDeleteTermStudentJoinLink(courseId, termId);
  const mutationError = regenerate.error ?? turnOff.error;

  // "Copied" is only feedback for the click, so it fades back after a moment.
  useEffect(() => {
    if (copyState !== "copied") return;
    const timeout = setTimeout(() => setCopyState("idle"), 2000);
    return () => clearTimeout(timeout);
  }, [copyState]);

  const url = link?.token ? studentJoinLinkUrl(link.token) : null;

  const handleCopy = () => {
    if (!url) return;
    // The clipboard API needs a secure context and may be blocked; the field
    // stays selectable, so the link can still be copied by hand.
    navigator.clipboard.writeText(url).then(
      () => setCopyState("copied"),
      () => setCopyState("failed"),
    );
  };

  const handleConfirm = () => {
    const mutation = confirm === "regenerate" ? regenerate : turnOff;
    mutation.mutate(undefined, { onSuccess: () => setConfirm(null) });
  };

  return (
    <Card>
      <CardTitle>{termActionText.studentJoinLink.title}</CardTitle>

      {mutationError && (
        <Alert className="mb-4" title="Could not change the join link">
          {getErrorMessage(mutationError)}
        </Alert>
      )}

      {isLoading ? (
        <p className="text-gray-500">Loading…</p>
      ) : error ? (
        <Alert title="Could not load the join link">
          {getErrorMessage(error)}
        </Alert>
      ) : !link || !url ? (
        <>
          <p className="mb-4 text-sm text-gray-500">
            Students can't join this semester with a link.
          </p>
          <Button
            type="button"
            variant="primary"
            onClick={() => setDialogOpen(true)}
          >
            Turn on link
          </Button>
        </>
      ) : (
        <>
          <div className="flex items-center gap-2">
            <input
              type="text"
              readOnly
              value={url}
              aria-label="Student join link"
              onFocus={(e) => e.target.select()}
              className="min-w-0 flex-1 px-3 py-2.5 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:outline-none focus:ring-2 focus:ring-hbrs-dark-blue"
            />
            <Button type="button" variant="secondary" onClick={handleCopy}>
              <span className="flex items-center gap-1.5">
                {copyState === "copied" ? (
                  <Check className="size-4" />
                ) : (
                  <Copy className="size-4" />
                )}
                {copyState === "copied" ? "Copied" : "Copy"}
              </span>
            </Button>
          </div>
          {copyState === "failed" && (
            <p className="text-xs text-red-600 mt-1">
              Your browser blocked copying. Select the link in the field and
              copy it yourself.
            </p>
          )}

          {isStudentJoinLinkExpired(link) && (
            <Alert variant="warning" className="mt-4">
              This link has expired, so students can't join with it. Change the
              expiry to make it work again.
            </Alert>
          )}

          <p className="mt-3 text-sm text-gray-500">
            {describeStudentJoinLinkExpiry(link)}{" "}
            <button
              type="button"
              onClick={() => setDialogOpen(true)}
              className="text-hbrs-dark-blue hover:underline"
            >
              Change
            </button>
          </p>

          <div className="mt-4 flex flex-wrap gap-2">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setConfirm("regenerate")}
            >
              Regenerate
            </Button>
            <Button
              type="button"
              variant="danger"
              onClick={() => setConfirm("turn-off")}
            >
              Turn off
            </Button>
          </div>
        </>
      )}

      {dialogOpen && (
        <StudentJoinLinkDialog
          courseId={courseId}
          termId={termId}
          isOn={!!link?.token}
          expiresAt={link?.token ? (link.expires_at ?? null) : accessEnd}
          onClose={() => setDialogOpen(false)}
        />
      )}

      <ConfirmDialog
        open={confirm === "regenerate"}
        onClose={() => setConfirm(null)}
        title="Regenerate the join link?"
        message="The current link stops working right away. Students who haven't joined yet need the new link."
        confirmText={regenerate.isPending ? "Regenerating…" : "Regenerate"}
        variant="destructive"
        onConfirm={handleConfirm}
        isConfirming={regenerate.isPending}
      />
      <ConfirmDialog
        open={confirm === "turn-off"}
        onClose={() => setConfirm(null)}
        title="Turn off the join link?"
        message="Students can no longer join with the current link. Turning it on again creates a new link."
        confirmText={turnOff.isPending ? "Turning off…" : "Turn off"}
        variant="destructive"
        onConfirm={handleConfirm}
        isConfirming={turnOff.isPending}
      />
    </Card>
  );
}
