import type { StudentJoinInfo } from "@api/types";
import { formatDateTime } from "@/lib/dateTime";

/** "Data Science, ws2026": how the join page names the semester. */
export function joinTargetName(info: StudentJoinInfo): string {
  return `${info.course_name}, ${info.term_id}`;
}

/** A sentence saying what joining means for the user right now. */
export function describeJoinStatus(info: StudentJoinInfo): string {
  const { student_access_start: start, student_access_end: end } = info;
  switch (info.status) {
    case "open":
      return end
        ? `You can start notebook servers until ${formatDateTime(end)}.`
        : "You can start notebook servers right away.";
    case "not_yet_open":
      return `You can start notebook servers from ${formatDateTime(start!)}.`;
    case "ended":
      return "This semester has ended, so it can no longer be joined.";
    case "already_member":
      return "You are already a member of this semester.";
  }
}

/** What the page says once the user has joined. */
export function describeJoined(info: StudentJoinInfo): string {
  const joined = `You've joined ${joinTargetName(info)}.`;
  if (info.status === "not_yet_open") {
    return `${joined} You can start notebook servers from ${formatDateTime(info.student_access_start!)}.`;
  }
  return `${joined} Taking you to start a notebook server…`;
}
