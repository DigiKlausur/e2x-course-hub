import { useId } from "react";
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

const options = [
  {
    restricted: false,
    label: "Unrestricted",
    hint: "Students can start notebook servers at any time.",
  },
  {
    restricted: true,
    label: "Restricted",
    hint: "Students can start notebook servers only between an opening and a closing time.",
  },
];

/** The restricted / unrestricted choice, with the opening and closing times once restricted. */
export function StudentAccessPeriodFields({
  value,
  onChange,
  disabled,
}: Props) {
  const error = accessPeriodDraftError(value);
  const name = useId();

  return (
    <div>
      <fieldset>
        <legend className="text-sm font-semibold">Student access</legend>
        <p className="text-xs text-gray-500 mb-2">Staff are not restricted.</p>
        <div className="grid gap-2">
          {options.map((option) => (
            <label
              key={option.label}
              className="flex cursor-pointer items-start gap-2 text-sm text-gray-700"
            >
              <input
                type="radio"
                name={name}
                checked={value.restricted === option.restricted}
                onChange={() =>
                  onChange({ ...value, restricted: option.restricted })
                }
                disabled={disabled}
                className="mt-0.5 accent-hbrs-dark-blue"
              />
              <span>
                <span className="font-medium">{option.label}</span>
                <span className="block text-xs text-gray-500">
                  {option.hint}
                </span>
              </span>
            </label>
          ))}
        </div>
      </fieldset>

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
