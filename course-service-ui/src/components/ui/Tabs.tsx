import type { ReactNode } from "react";

export interface TabItem<T extends string> {
  id: T;
  label: string;
  /** Shown next to the label, e.g. the number of members. */
  badge?: ReactNode;
}

interface TabsProps<T extends string> {
  tabs: TabItem<T>[];
  activeId: T;
  onChange: (id: T) => void;
}

/** Tabs switched by local state, e.g. within a card or modal. For page tabs that change the URL, use `TabBar`. */
export function Tabs<T extends string>({
  tabs,
  activeId,
  onChange,
}: TabsProps<T>) {
  return (
    <div className="border-b border-gray-200">
      <div role="tablist" className="flex flex-wrap gap-1">
        {tabs.map((tab) => {
          const isActive = tab.id === activeId;
          return (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={isActive}
              onClick={() => onChange(tab.id)}
              className={`inline-flex items-center gap-2 rounded-t-lg border-b-2 px-4 py-2.5 text-sm font-semibold transition-colors ${
                isActive
                  ? "border-hbrs-dark-blue text-hbrs-dark-blue"
                  : "border-transparent text-gray-500 hover:text-gray-800"
              }`}
            >
              <span>{tab.label}</span>
              {tab.badge !== undefined && (
                <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                  {tab.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
