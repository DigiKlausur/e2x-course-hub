/**
 * Conversions between the API's timestamps (ISO 8601 with timezone, UTC) and
 * what the UI shows or edits (the browser's local time).
 */

const displayFormat = new Intl.DateTimeFormat(undefined, {
  dateStyle: "medium",
  timeStyle: "short",
});

/** A timestamp for display in local time. */
export function formatDateTime(iso: string): string {
  return displayFormat.format(new Date(iso));
}

const pad = (n: number) => String(n).padStart(2, "0");

/** A timestamp as the value of a `datetime-local` input, or `""` when empty. */
export function toDateTimeLocal(iso: string | null | undefined): string {
  if (!iso) return "";
  const d = new Date(iso);
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

/** A `datetime-local` value (local time) as a UTC timestamp, or `null` when empty. */
export function fromDateTimeLocal(value: string): string | null {
  return value ? new Date(value).toISOString() : null;
}
