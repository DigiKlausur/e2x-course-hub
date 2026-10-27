import { Switch } from "@components/ui/Switch";
import { DateTimeField } from "@components/ui/DateTimeField";
import {
  accessPeriodDraftError,
  type AccessPeriodDraft,
} from "@domain/accessPeriod";

interface Props {
  value: AccessPeriodDraft;
  onChange: (value: AccessPeriodDraft) => void;
  disabled?: boolean;
}

/** The "Restrict student access" switch, with the opening and closing times once on. */
export function StudentAccessPeriodFields({
  value,
  onChange,
  disabled,
}: Props) {
  const error = accessPeriodDraftError(value);

  return (
    <div>
      <Switch
        checked={value.restricted}
        onChange={(restricted) => onChange({ ...value, restricted })}
        label="Restrict student access"
        title="Limit when students can start notebook servers for this semester. Staff are not restricted."
      />

      {value.restricted && (
        <>
          {/* 00:05 rather than 00:00, which reads as belonging to the day before. */}
          <div className="mt-4 grid gap-4">
            <DateTimeField
              label="Opens"
              value={value.start}
              onChange={(start) => onChange({ ...value, start })}
              defaultTime="00:05"
              hint="Leave empty to open immediately."
              disabled={disabled}
            />
            <DateTimeField
              label="Closes"
              value={value.end}
              onChange={(end) => onChange({ ...value, end })}
              defaultTime="23:55"
              hint="Leave empty to keep it open indefinitely."
              disabled={disabled}
            />
          </div>
          {error && <p className="text-xs text-red-600 mt-2">{error}</p>}
        </>
      )}
    </div>
  );
}
