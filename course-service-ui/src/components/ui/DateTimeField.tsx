import { MINUTE_STEP, pad } from "@/lib/dateTime";

const HOURS = Array.from({ length: 24 }, (_, h) => pad(h));
const MINUTES = Array.from({ length: 60 / MINUTE_STEP }, (_, i) =>
  pad(i * MINUTE_STEP),
);

interface Props {
  label: string;
  /** A `datetime-local` value ("YYYY-MM-DDTHH:mm"), or `""` when empty. */
  value: string;
  onChange: (value: string) => void;
  /** The time ("HH:mm") used when a date is picked while the field is empty. */
  defaultTime: string;
  hint?: string;
  disabled?: boolean;
}

/**
 * A date, then a time in `MINUTE_STEP` steps. The time can only be chosen once
 * a date is set, so the field is either empty or complete. Values off the step
 * grid are not supported; `toDateTimeLocal` rounds them down.
 */
export function DateTimeField({
  label,
  value,
  onChange,
  defaultTime,
  hint,
  disabled,
}: Props) {
  const [date = "", time = ""] = value ? value.split("T") : [];
  const [hour = "", minute = ""] = time ? time.split(":") : [];

  const setDate = (newDate: string) =>
    onChange(newDate ? `${newDate}T${time || defaultTime}` : "");
  const setTime = (newHour: string, newMinute: string) =>
    onChange(`${date}T${newHour}:${newMinute}`);

  const controlClass =
    "px-3 py-2.5 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-hbrs-dark-blue disabled:bg-gray-50 disabled:text-gray-500";

  return (
    <div>
      <label className="block text-sm font-semibold mb-1.5">{label}</label>
      <div className="flex items-center gap-2">
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          disabled={disabled}
          aria-label={`${label} date`}
          className={`${controlClass} min-w-0 flex-1`}
        />
        <select
          value={hour}
          onChange={(e) => setTime(e.target.value, minute)}
          disabled={disabled || !date}
          aria-label={`${label} hour`}
          className={controlClass}
        >
          {!date && <option value="">--</option>}
          {HOURS.map((h) => (
            <option key={h} value={h}>
              {h}
            </option>
          ))}
        </select>
        <span className="text-gray-500">:</span>
        <select
          value={minute}
          onChange={(e) => setTime(hour, e.target.value)}
          disabled={disabled || !date}
          aria-label={`${label} minute`}
          className={controlClass}
        >
          {!date && <option value="">--</option>}
          {MINUTES.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
      </div>
      <div className="mt-1 flex justify-between gap-2 text-xs">
        {hint && <p className="text-gray-500">{hint}</p>}
        {date && !disabled && (
          <button
            type="button"
            onClick={() => onChange("")}
            className="text-hbrs-dark-blue hover:underline"
          >
            Clear
          </button>
        )}
      </div>
    </div>
  );
}
