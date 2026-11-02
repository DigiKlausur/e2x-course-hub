import type { UsernameFormat } from "@config";

/** Whether the username matches the whole pattern, like Python's `re.fullmatch`. */
const matches = (format: UsernameFormat, username: string): boolean =>
  new RegExp(`^(?:${format.pattern})$`).test(username);

/** The usernames that match none of the formats. Without formats, every username is valid. */
export const invalidUsernames = (
  usernames: string[],
  formats: UsernameFormat[],
): string[] =>
  formats.length === 0
    ? []
    : usernames.filter((u) => !formats.some((f) => matches(f, u)));
