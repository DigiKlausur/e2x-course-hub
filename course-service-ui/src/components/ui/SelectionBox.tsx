import type { ReactNode } from "react";

interface SelectionBoxProps {
  label: string;
  title: string;
  description?: string;
  onChangeClick: () => void;
  infoContent?: ReactNode;
}

export function SelectionBox({
  label,
  title,
  description,
  onChangeClick,
  infoContent,
}: SelectionBoxProps) {
  return (
    <div className="mb-5">
      <label className="block text-sm font-semibold mb-2">{label}</label>
      <div className="flex justify-between items-center p-4 border border-gray-200 rounded-xl bg-gray-50">
        <div>
          <div className="font-semibold">{title}</div>
          {description && (
            <div className="text-sm text-gray-500 mt-0.5">{description}</div>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onChangeClick}
            className="bg-white text-hbrs-dark-blue border border-hbrs-dark-blue rounded-lg px-4 py-2 text-sm font-semibold hover:bg-hbrs-light-blue transition-colors"
          >
            Change
          </button>
        </div>
      </div>
      {infoContent && (
        <div className="mt-2 text-sm text-gray-500">{infoContent}</div>
      )}
    </div>
  );
}
