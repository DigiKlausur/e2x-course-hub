import type { StudentJoinLink } from "@api/types";
import { formatDateTime } from "@/lib/dateTime";

/** Whether the link no longer works at `now`. Mirrors the backend: the expiry is exclusive. */
export function isStudentJoinLinkExpired(
  link: StudentJoinLink,
  now: Date = new Date(),
): boolean {
  return !!link.expires_at && now >= new Date(link.expires_at);
}

/** A sentence saying until when the link works. */
export function describeStudentJoinLinkExpiry(
  link: StudentJoinLink,
  now: Date = new Date(),
): string {
  if (!link.expires_at) return "The link works until it is turned off.";
  if (isStudentJoinLinkExpired(link, now)) {
    return `The link expired on ${formatDateTime(link.expires_at)}.`;
  }
  return `The link works until ${formatDateTime(link.expires_at)}.`;
}
