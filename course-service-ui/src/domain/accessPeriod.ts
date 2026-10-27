import type { StudentAccessPeriod } from "@api/types";
import {
  formatDateTime,
  fromDateTimeLocal,
  toDateTimeLocal,
} from "@/lib/dateTime";

/**
 * Whether students can start notebook servers at `now`. Mirrors the backend check:
 * the start is inclusive, the end exclusive, and an empty bound is no limit.
 */
function accessPeriodStatus(
  period: StudentAccessPeriod,
  now: Date,
): "upcoming" | "open" | "closed" {
  const { student_access_start: start, student_access_end: end } = period;
  if (start && now < new Date(start)) return "upcoming";
  if (end && now >= new Date(end)) return "closed";
  return "open";
}

/** A sentence saying whether and when students can start notebook servers. */
export function describeAccessPeriod(
  period: StudentAccessPeriod,
  now: Date = new Date(),
): string {
  const { student_access_start: start, student_access_end: end } = period;
  const canStart = "Students can start notebook servers";
  switch (accessPeriodStatus(period, now)) {
    case "upcoming":
      return `${canStart} from ${formatDateTime(start!)}${end ? ` until ${formatDateTime(end)}` : ""}.`;
    case "closed":
      return `Students can no longer start notebook servers (closed ${formatDateTime(end!)}).`;
    case "open":
      return end
        ? `${canStart} until ${formatDateTime(end)}.`
        : `${canStart} at any time.`;
  }
}

/** The form state of an access period; `start` and `end` are `datetime-local` values. */
export interface AccessPeriodDraft {
  restricted: boolean;
  start: string;
  end: string;
}

export function toAccessPeriodDraft(
  period?: StudentAccessPeriod,
): AccessPeriodDraft {
  const start = toDateTimeLocal(period?.student_access_start);
  const end = toDateTimeLocal(period?.student_access_end);
  return { restricted: start !== "" || end !== "", start, end };
}

/** The draft as sent to the API; an unrestricted draft clears both bounds. */
export function fromAccessPeriodDraft(
  draft: AccessPeriodDraft,
): StudentAccessPeriod {
  if (!draft.restricted) {
    return { student_access_start: null, student_access_end: null };
  }
  return {
    student_access_start: fromDateTimeLocal(draft.start),
    student_access_end: fromDateTimeLocal(draft.end),
  };
}

/** Why the draft cannot be saved, or `null` when it can. */
export function accessPeriodDraftError(
  draft: AccessPeriodDraft,
): string | null {
  if (!draft.restricted) return null;
  if (!draft.start && !draft.end) {
    return "Set an opening time, a closing time, or both.";
  }
  // `datetime-local` values share one fixed format, so they compare as strings.
  if (draft.start && draft.end && draft.end <= draft.start) {
    return "The closing time must be after the opening time.";
  }
  return null;
}
