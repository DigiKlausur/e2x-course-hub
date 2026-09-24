import type {
  CourseCapabilities,
  CourseCollectionCapabilities,
} from "@api/types";
import type { CapabilityTextMap } from "./types";

export const courseCollectionCapabilityText = {
  createCourse: {
    label: "Create Course",
    description: "Set up a new course. You become its owner.",
  },
} satisfies CapabilityTextMap<CourseCollectionCapabilities>;

export const courseCapabilityText = {
  editMetadata: {
    label: "Edit Course Settings",
    description: "Change the course name and description.",
  },
  removeCourse: {
    label: "Delete course",
    description: "Permanently delete the course and all of its terms.",
  },
  selectEnvironment: {
    label: "Change runtime template",
    description:
      "These are the defaults applied when a new semester is created for this course. Changing them here does not affect existing semesters.",
  },
  addTerm: {
    label: "Create Semester",
    description:
      "Add a new semester to this course. It starts with the course's runtime template.",
  },
} satisfies CapabilityTextMap<CourseCapabilities>;
