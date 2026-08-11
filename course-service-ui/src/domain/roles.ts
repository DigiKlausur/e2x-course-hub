export const MembershipRole = {
  Admin: "admin",
  CourseOwner: "owner",
  CourseCreator: "course-creator",
  Instructor: "instructor",
  TeachingAssistant: "teaching-assistant",
  Student: "student",
  Observer: "observer",
} as const;

export type MembershipRole =
  (typeof MembershipRole)[keyof typeof MembershipRole];
