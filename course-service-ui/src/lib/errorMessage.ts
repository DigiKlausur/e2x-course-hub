import type { ApiError } from "@api/client";

/**
 * Turn a thrown request error into something worth showing a user.
 *
 * The service answers failures with RFC 9457 problem details and `client.ts`
 * already parses them, so prefer `detail` (the specific explanation, e.g. which
 * permission was missing) over `title` (the generic class of problem) over the
 * bare `Error.message`, which for a non-JSON response is only "HTTP 500".
 */
export function getErrorMessage(
  error: unknown,
  fallback = "Something went wrong. Please try again.",
): string {
  if (!error) return fallback;

  const response = (error as ApiError).response;
  if (response?.detail) return response.detail;
  if (response?.title) return response.title;

  const message = (error as Error)?.message;
  return message || fallback;
}

/** True when the request failed because the user lacks the required permission. */
export function isPermissionError(error: unknown): boolean {
  return (error as ApiError)?.response?.status === 403;
}
