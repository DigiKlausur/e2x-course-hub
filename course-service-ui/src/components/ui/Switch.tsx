interface SwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
  /** Shown as a tooltip, e.g. to explain what switching on does. */
  title?: string;
}

export function Switch({ checked, onChange, label, title }: SwitchProps) {
  return (
    <label
      title={title}
      className="inline-flex cursor-pointer items-center gap-2 text-sm text-gray-700"
    >
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors ${
          checked ? "bg-hbrs-dark-blue" : "bg-gray-300"
        }`}
      >
        <span
          className={`inline-block size-4 rounded-full bg-white shadow transition-transform ${
            checked ? "translate-x-4.5" : "translate-x-0.5"
          }`}
        />
      </button>
      {label}
    </label>
  );
}
