export const studentJoinKeys = {
  info: (token: string) => ["student-join", token] as const,
};
