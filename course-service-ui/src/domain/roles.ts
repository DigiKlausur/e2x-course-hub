export const MembershipRole = {
  Admin: "lms-admin",
  CourseOwner: "course-owner",
  CourseCreator: "course-creator",
  Instructor: "instructor",
  TeachingAssistant: "teaching-assistant",
  Student: "student",
  Observer: "observer",
} as const;

export type MembershipRole =
  (typeof MembershipRole)[keyof typeof MembershipRole];

export interface MemberLabels {
  singular: string;
  plural: string;
}

export const memberLabels = {
  [MembershipRole.Admin]: { singular: "LMS Admin", plural: "LMS Admins" },
  [MembershipRole.CourseCreator]: {
    singular: "Course Creator",
    plural: "Course Creators",
  },
  [MembershipRole.CourseOwner]: {
    singular: "Course Owner",
    plural: "Course Owners",
  },
  [MembershipRole.Instructor]: {
    singular: "Instructor",
    plural: "Instructors",
  },
  [MembershipRole.TeachingAssistant]: {
    singular: "Teaching Assistant",
    plural: "Teaching Assistants",
  },
  [MembershipRole.Student]: { singular: "Student", plural: "Students" },
  [MembershipRole.Observer]: { singular: "Observer", plural: "Observers" },
} satisfies Record<MembershipRole, MemberLabels>;
