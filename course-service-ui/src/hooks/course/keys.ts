export const courseKeys = {
  all: ["courses"] as const,

  detail: (courseId: string) => ["course", courseId] as const,

  terms: {
    all: (courseId: string) => ["course", courseId, "terms"] as const,

    detail: (courseId: string, termId: string) =>
      ["course", courseId, "terms", termId] as const,

    // Nested under the term, so invalidating or removing the term covers it too.
    studentJoinLink: (courseId: string, termId: string) =>
      ["course", courseId, "terms", termId, "student-join-link"] as const,
  },
};
