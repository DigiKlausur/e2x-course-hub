import type { TermActions } from "@api/types";
import { MembershipRole } from "@domain/roles";
import { memberListText } from "./membership";
import type { ActionTextMap } from "./types";

export const termActionText = {
  view: {
    label: "View semester",
    description: "Open the semester and see its details.",
  },
  remove: {
    label: "Delete Semester",
    description:
      "Permanently delete the semester and remove all of its members.",
  },
  environment: {
    title: "Environment",
    select: {
      label: "Change semester runtime",
      description:
        "Choose the notebook image and resources used for this semester.",
    },
  },
  spawn: {
    title: "Start environments",
    student: {
      label: "Student environment",
      description: "Start a notebook server with the student environment.",
    },
    grader: {
      label: "Grader environment",
      description: "Start a notebook server with the grader environment.",
    },
    readonlyGrader: {
      label: "Read-only grader environment",
      description:
        "Start the grader environment with the course directory read-only.",
    },
  },
  members: {
    title: "Members",
    instructors: memberListText(MembershipRole.Instructor),
    teachingAssistants: memberListText(MembershipRole.TeachingAssistant),
    students: memberListText(MembershipRole.Student),
    observers: memberListText(MembershipRole.Observer),
  },
} satisfies ActionTextMap<TermActions>;
