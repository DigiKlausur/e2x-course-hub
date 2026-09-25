import type { CourseActions, LmsActions } from "@api/types";
import type { ActionTextMap } from "./types";

export const lmsActionText = {
  courses: {
    create: {
      label: "Create Course",
      description: "Set up a new course. You become its owner.",
    },
  },
} satisfies ActionTextMap<LmsActions>;

export const courseActionText = {
  metadata: {
    edit: {
      label: "Edit Course Settings",
      description: "Change the course name and description.",
    },
  },
  remove: {
    label: "Delete course",
    description: "Permanently delete the course and all of its terms.",
  },
  environment: {
    select: {
      label: "Change runtime template",
      description:
        "These are the defaults applied when a new semester is created for this course. Changing them here does not affect existing semesters.",
    },
  },
  terms: {
    add: {
      label: "Create Semester",
      description:
        "Add a new semester to this course. It starts with the course's runtime template.",
    },
  },
} satisfies ActionTextMap<CourseActions>;
