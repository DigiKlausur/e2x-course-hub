import { useState } from "react";
import { Modal } from "@components/ui/Modal";
import { Button } from "@components/ui/Button";
import { Alert } from "@components/ui/Alert";
import { Switch } from "@components/ui/Switch";
import { Tabs } from "@components/ui/Tabs";
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

/** Where the role would be granted, so the explanation can name it. */
export interface RoleContext {
  courseId: string;
  termId?: string;
}

interface Props {
  role: MembershipRole;
  open: boolean;
  onClose: () => void;
  context?: RoleContext;
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

/**
 * Which LMS, course or semester a level's actions apply to, depending on the
 * level the role is granted at (the first entry of its LEVEL_ORDER). Names the
 * course and semester when the context has them.
 */
function scopeLine(roleLevel: Level, level: Level, context?: RoleContext) {
  if (level === "lms") return "Across the whole LMS.";
  const course = context?.courseId;
  const term = context?.termId;

  switch (roleLevel) {
    case "term":
      if (level === "term") {
        return course && term
          ? `In semester ${term} of course ${course}.`
          : "In the semester they are added to.";
      }
      return course
        ? `In course ${course}.`
        : "In the course of that semester.";
    case "course":
      if (level === "course") {
        return course
          ? `In course ${course}.`
          : "In the course they are added to.";
      }
      return course
        ? `In every semester of course ${course}.`
        : "In every semester of that course.";
    case "lms":
      // LMS roles apply everywhere, whatever page the modal is opened from.
      return level === "course"
        ? "In every course."
        : "In every semester of every course.";
  }
}

function levelList(
  data: RoleActionsResponse,
  level: Level,
  showDenied: boolean,
): ReactNode {
  switch (level) {
    case "lms":
      return (
        <ActionList
          actions={data.lms}
          texts={lmsActionText}
          showDenied={showDenied}
        />
      );
    case "course":
      return (
        <ActionList
          actions={data.course}
          texts={courseActionText}
          showDenied={showDenied}
        />
      );
    case "term":
      return (
        <ActionList
          actions={data.term}
          texts={termActionText}
          showDenied={showDenied}
        />
      );
  }
}

/** What a role can do, and on request what it can't, e.g. before adding someone to it. */
export function RoleActionsModal({ role, open, onClose, context }: Props) {
  const { data, isLoading, error } = useRoleActions(role, open);
  const [showRestrictions, setShowRestrictions] = useState(false);
  const [selectedLevel, setSelectedLevel] = useState<Level | null>(null);
  const labels = memberLabels[role];
  const roleLevel = LEVEL_ORDER[role][0];
  // Levels where the role cannot do anything would only list what it can't do.
  const levels = data
    ? LEVEL_ORDER[role].filter((level) => hasAny(data[level]))
    : [];
  const activeLevel =
    selectedLevel && levels.includes(selectedLevel) ? selectedLevel : levels[0];

  // Always open compact, on the level the role is granted at.
  const close = () => {
    setShowRestrictions(false);
    setSelectedLevel(null);
    onClose();
  };

  return (
    <Modal
      open={open}
      onClose={close}
      title={`What a ${labels.singular} can do`}
      fixedHeight
      footer={
        <>
          {/* mr-auto pushes the switch to the left, opposite "Close". */}
          <div className="mr-auto flex items-center">
            <Switch
              checked={showRestrictions}
              onChange={setShowRestrictions}
              label="Show restrictions"
              title={`Also list what a ${labels.singular} can't do.`}
            />
          </div>
          <Button variant="secondary" onClick={close}>
            Close
          </Button>
        </>
      }
    >
      {isLoading && <p className="text-sm text-gray-500">Loading…</p>}
      {error && (
        <Alert title="Could not load the role">{getErrorMessage(error)}</Alert>
      )}
      {data && activeLevel && (
        <>
          {levels.length > 1 && (
            <Tabs
              tabs={levels.map((level) => ({
                id: level,
                label: LEVEL_TITLES[level],
              }))}
              activeId={activeLevel}
              onChange={setSelectedLevel}
            />
          )}
          <p className="mt-3 mb-4 text-sm text-gray-500">
            {scopeLine(roleLevel, activeLevel, context)}
          </p>
          {levelList(data, activeLevel, showRestrictions)}
        </>
      )}
    </Modal>
  );
}
