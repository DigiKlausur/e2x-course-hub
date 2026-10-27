import { useState } from "react";
import { Card, CardTitle } from "@components/ui/Card";
import { Badge } from "@components/ui/Badge";
import { Button } from "@components/ui/Button";
import { Alert } from "@components/ui/Alert";
import { useUpdateTermAccessPeriod } from "@hooks/course";
import { getErrorMessage } from "@/lib/errorMessage";
import { fromDateTimeLocal, toDateTimeLocal } from "@/lib/dateTime";
import { termActionText } from "@domain/actions";
import {
  accessPeriodStatus,
  accessPeriodStatusLabel,
  type AccessPeriodStatus,
} from "@domain/accessPeriod";
import type { StudentAccessPeriod } from "@api/types";

const statusBadge: Record<
  AccessPeriodStatus,
  "default" | "active" | "archived"
> = {
  upcoming: "default",
  open: "active",
  closed: "archived",
};

interface Props {
  courseId: string;
  termId: string;
  accessPeriod: StudentAccessPeriod;
}

export function StudentAccessPeriodCard({
  courseId,
  termId,
  accessPeriod,
}: Props) {
  const update = useUpdateTermAccessPeriod(courseId, termId);

  // `null` means "untouched, follow the server value"; `""` is a cleared field,
  // which means "no limit" on that side.
  const [start, setStart] = useState<string | null>(null);
  const [end, setEnd] = useState<string | null>(null);

  const currentStart =
    start ?? toDateTimeLocal(accessPeriod.student_access_start);
  const currentEnd = end ?? toDateTimeLocal(accessPeriod.student_access_end);

  // `datetime-local` values share one fixed format, so they compare as strings.
  const endNotAfterStart =
    currentStart !== "" && currentEnd !== "" && currentEnd <= currentStart;
  const isDirty = start !== null || end !== null;

  const status = accessPeriodStatus(accessPeriod);

  const handleSave = () => {
    update.mutate(
      {
        student_access_start: fromDateTimeLocal(currentStart),
        student_access_end: fromDateTimeLocal(currentEnd),
      },
      // Drop the local edits so the form follows the server again.
      {
        onSuccess: () => {
          setStart(null);
          setEnd(null);
        },
      },
    );
  };

  const fieldClass =
    "w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-hbrs-dark-blue disabled:bg-gray-50 disabled:text-gray-500";

  return (
    <Card>
      <div className="flex items-center justify-between">
        <CardTitle>{termActionText.accessPeriod.title}</CardTitle>
        <Badge variant={statusBadge[status]}>
          {accessPeriodStatusLabel[status]}
        </Badge>
      </div>
      <p className="text-sm text-gray-500 mb-4">
        {termActionText.accessPeriod.edit.description}
      </p>

      {update.error && (
        <Alert className="mb-5" title="Could not save the access period">
          {getErrorMessage(update.error)}
        </Alert>
      )}

      <div className="mb-5">
        <label className="block text-sm font-semibold mb-2">Opens</label>
        <input
          type="datetime-local"
          value={currentStart}
          onChange={(e) => setStart(e.target.value)}
          disabled={update.isPending}
          className={fieldClass}
        />
        <p className="text-xs text-gray-500 mt-1">
          Leave empty to open immediately.
        </p>
      </div>

      <div className="mb-5">
        <label className="block text-sm font-semibold mb-2">Closes</label>
        <input
          type="datetime-local"
          value={currentEnd}
          onChange={(e) => setEnd(e.target.value)}
          disabled={update.isPending}
          className={fieldClass}
        />
        {endNotAfterStart ? (
          <p className="text-xs text-red-600 mt-1">
            The closing time must be after the opening time.
          </p>
        ) : (
          <p className="text-xs text-gray-500 mt-1">
            Leave empty to keep it open indefinitely.
          </p>
        )}
      </div>

      <Button
        variant="primary"
        onClick={handleSave}
        disabled={update.isPending || !isDirty || endNotAfterStart}
      >
        {update.isPending ? "Saving…" : "Save Changes"}
      </Button>
    </Card>
  );
}
