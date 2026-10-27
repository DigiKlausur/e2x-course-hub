import type { StudentAccessPeriod } from "@api/types";
import { formatDateTime } from "@/lib/dateTime";

export type AccessPeriodStatus = "upcoming" | "open" | "closed";

/**
 * Whether students can start the semester at `now`. Mirrors the backend check:
 * the start is inclusive, the end exclusive, and an empty bound is no limit.
 */
export function accessPeriodStatus(
  period: StudentAccessPeriod,
  now: Date = new Date(),
): AccessPeriodStatus {
  const { student_access_start: start, student_access_end: end } = period;
  if (start && now < new Date(start)) return "upcoming";
  if (end && now >= new Date(end)) return "closed";
  return "open";
}

export const accessPeriodStatusLabel: Record<AccessPeriodStatus, string> = {
  upcoming: "Not open yet",
  open: "Open",
  closed: "Closed",
};

/** A one-line summary, e.g. "Opens 2 Nov 2026, 09:00" or "Open, no limit". */
export function describeAccessPeriod(
  period: StudentAccessPeriod,
  now: Date = new Date(),
): string {
  const { student_access_start: start, student_access_end: end } = period;
  switch (accessPeriodStatus(period, now)) {
    case "upcoming":
      return `Opens ${formatDateTime(start!)}`;
    case "closed":
      return `Closed since ${formatDateTime(end!)}`;
    case "open":
      return end ? `Open until ${formatDateTime(end)}` : "Open, no limit";
  }
}
