import type { CourseActions, LmsActions } from "@api/types";
import { MembershipRole } from "@domain/roles";
import { memberListText } from "./membership";
import type { ActionTextMap } from "./types";

export const lmsActionText = {
  courses: {
    title: "Courses",
    create: {
      label: "Create Course",
      description: "Set up a new course. You become its owner.",
    },
  },
  members: {
    title: "Members",
    lmsAdmins: memberListText(MembershipRole.Admin),
    courseCreators: memberListText(MembershipRole.CourseCreator),
  },
  catalogs: {
    title: "Catalogs",
    images: {
      title: "Images",
      view: {
        label: "View image catalog",
        description: "See the notebook images that courses can choose from.",
      },
      manage: {
        label: "Manage image catalog",
        description: "Change the notebook images that courses can choose from.",
      },
    },
    resources: {
      title: "Resources",
      view: {
        label: "View resource catalog",
        description: "See the resource tiers that courses can choose from.",
      },
      manage: {
        label: "Manage resource catalog",
        description: "Change the resource tiers that courses can choose from.",
      },
    },
    profiles: {
      title: "Profiles",
      view: {
        label: "View profile catalog",
        description: "See the profiles that courses can choose from.",
      },
      manage: {
        label: "Manage profile catalog",
        description: "Change the profiles that courses can choose from.",
      },
    },
  },
} satisfies ActionTextMap<LmsActions>;

export const courseActionText = {
  view: {
    label: "View course",
    description: "Open the course and see its semesters.",
  },
  remove: {
    label: "Delete course",
    description: "Permanently delete the course and all of its semesters.",
  },
  metadata: {
    title: "Course Settings",
    view: {
      label: "View Course Settings",
      description: "See the course name and description.",
    },
    edit: {
      label: "Edit Course Settings",
      description: "Change the course name and description.",
    },
  },
  environment: {
    title: "Environment",
    select: {
      label: "Change runtime template",
      description:
        "These are the defaults applied when a new semester is created for this course. Changing them here does not affect existing semesters.",
    },
  },
  terms: {
    title: "Semesters",
    add: {
      label: "Create Semester",
      description:
        "Add a new semester to this course. It starts with the course's runtime template.",
    },
  },
  members: {
    title: "Members",
    courseOwners: memberListText(MembershipRole.CourseOwner),
  },
} satisfies ActionTextMap<CourseActions>;
