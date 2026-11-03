import { config } from "@config";

/**
 * The full URL of a student join link, as staff share it. It points at the
 * join page route (`/join/:token`), resolved against the page's origin because
 * `baseUrl` is usually only a path.
 */
export function studentJoinLinkUrl(token: string): string {
  const base = config.baseUrl.replace(/\/$/, "");
  return new URL(`${base}/join/${token}`, window.location.origin).href;
}
