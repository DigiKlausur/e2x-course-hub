import { MembershipRole } from "@domain/roles";

export const membershipQueryKeys = {
  all: ["membership"] as const,
  hub: {
    all: () => [...membershipQueryKeys.all, "hub"] as const,
    roles: {
      [MembershipRole.Admin]: () =>
        [...membershipQueryKeys.hub.all(), MembershipRole.Admin] as const,
      [MembershipRole.CourseCreator]: () =>
        [
          ...membershipQueryKeys.hub.all(),
          MembershipRole.CourseCreator,
        ] as const,
    },
  },
  courses: {
    all: (courseId: string) =>
      [...membershipQueryKeys.all, "courses", courseId] as const,
    roles: {
      [MembershipRole.CourseOwner]: (courseId: string) =>
        [
          ...membershipQueryKeys.courses.all(courseId),
          MembershipRole.CourseOwner,
        ] as const,
    },
  },
  terms: {
    all: (courseId: string, termId: string) =>
      [...membershipQueryKeys.all, "terms", courseId, termId] as const,
    roles: {
      [MembershipRole.Instructor]: (courseId: string, termId: string) =>
        [
          ...membershipQueryKeys.terms.all(courseId, termId),
          MembershipRole.Instructor,
        ] as const,
      [MembershipRole.TeachingAssistant]: (courseId: string, termId: string) =>
        [
          ...membershipQueryKeys.terms.all(courseId, termId),
          MembershipRole.TeachingAssistant,
        ] as const,
      [MembershipRole.Student]: (courseId: string, termId: string) =>
        [
          ...membershipQueryKeys.terms.all(courseId, termId),
          MembershipRole.Student,
        ] as const,
      [MembershipRole.Observer]: (courseId: string, termId: string) =>
        [
          ...membershipQueryKeys.terms.all(courseId, termId),
          MembershipRole.Observer,
        ] as const,
    },
  },
};
