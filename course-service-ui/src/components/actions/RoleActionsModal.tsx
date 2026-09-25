import { Modal } from "@components/ui/Modal";
import { Button } from "@components/ui/Button";
import { Alert } from "@components/ui/Alert";
import { ActionList } from "./ActionList";
import { useRoleActions } from "@hooks/roles";
import { getErrorMessage } from "@/lib/errorMessage";
import {
  courseActionText,
  hasAny,
  lmsActionText,
  termActionText,
} from "@domain/actions";
import { MembershipRole, memberLabels } from "@domain/roles";
import type { RoleActionsResponse } from "@api/types";
import type { ReactNode } from "react";

interface Props {
  role: MembershipRole;
  open: boolean;
  onClose: () => void;
}

type Level = "lms" | "course" | "term";

// Start at the level the role is granted at, then the others.
const LEVEL_ORDER: Record<MembershipRole, Level[]> = {
  [MembershipRole.Admin]: ["lms", "course", "term"],
  [MembershipRole.CourseCreator]: ["lms", "course", "term"],
  [MembershipRole.CourseOwner]: ["course", "term", "lms"],
  [MembershipRole.Instructor]: ["term", "course", "lms"],
  [MembershipRole.TeachingAssistant]: ["term", "course", "lms"],
  [MembershipRole.Student]: ["term", "course", "lms"],
  [MembershipRole.Observer]: ["term", "course", "lms"],
};

const LEVEL_TITLES: Record<Level, string> = {
  lms: "LMS",
  course: "Course",
  term: "Semester",
};

function levelList(data: RoleActionsResponse, level: Level): ReactNode {
  switch (level) {
    case "lms":
      return <ActionList actions={data.lms} texts={lmsActionText} showDenied />;
    case "course":
      return (
        <ActionList actions={data.course} texts={courseActionText} showDenied />
      );
    case "term":
      return (
        <ActionList actions={data.term} texts={termActionText} showDenied />
      );
  }
}

/** What a role can and cannot do, e.g. before adding someone to it. */
export function RoleActionsModal({ role, open, onClose }: Props) {
  const { data, isLoading, error } = useRoleActions(role, open);
  const labels = memberLabels[role];
  // Levels where the role cannot do anything would only list what it can't do.
  const levels = data
    ? LEVEL_ORDER[role].filter((level) => hasAny(data[level]))
    : [];

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`What a ${labels.singular} can do`}
      footer={
        <Button variant="secondary" onClick={onClose}>
          Close
        </Button>
      }
    >
      {isLoading && <p className="text-sm text-gray-500">Loading…</p>}
      {error && (
        <Alert title="Could not load the role">{getErrorMessage(error)}</Alert>
      )}
      <div className="space-y-6">
        {data &&
          levels.map((level) => (
            <section key={level}>
              <h3 className="mb-3 text-sm font-semibold text-gray-900">
                {LEVEL_TITLES[level]}
              </h3>
              {levelList(data, level)}
            </section>
          ))}
      </div>
    </Modal>
  );
}
