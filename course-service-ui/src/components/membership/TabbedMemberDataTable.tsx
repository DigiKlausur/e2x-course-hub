import { useMemo, useState } from "react";

import { Button } from "@components/ui/Button";
import { Card } from "@components/ui/Card";
import { MemberDataTable } from "./MemberDataTable";
import type { CurrentUser } from "@api/types";

export interface MemberTabConfig {
  id: string;
  label: string;
  usernames: string[];
  isLoading?: boolean;
  selected: Set<string>;
  onSelect: (username: string) => void;
  onSelectAll: (select: boolean, usernames: string[]) => void;
  onRemove: (username: string) => void;
  onRemoveSelected: () => void;
  canRemove?: boolean;
  removeLabel?: string;
  canAdd?: boolean;
  addLabel?: string;
  onAddClick?: () => void;
  isMutating?: boolean;
}

export interface TabbedMemberDataTableProps {
  tabs: MemberTabConfig[];
  currentUser: CurrentUser;
}

export function TabbedMemberDataTable({
  tabs,
  currentUser,
}: TabbedMemberDataTableProps) {
  const [activeTabId, setActiveTabId] = useState<string>(tabs[0]?.id ?? "");

  const activeTab = useMemo(
    () => tabs.find((tab) => tab.id === activeTabId) ?? tabs[0],
    [tabs, activeTabId],
  );

  if (!activeTab) return null;

  return (
    <Card className="mb-0">
      {/* Tab bar */}
      <div className="border-b border-gray-200">
        <div className="flex flex-wrap gap-1">
          {tabs.map((tab) => {
            const isActive = tab.id === activeTab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTabId(tab.id)}
                className={`inline-flex items-center gap-2 rounded-t-lg border-b-2 px-4 py-2.5 text-sm font-semibold transition-colors ${
                  isActive
                    ? "border-hbrs-dark-blue text-hbrs-dark-blue"
                    : "border-transparent text-gray-500 hover:text-gray-800"
                }`}
              >
                <span>{tab.label}</span>
                <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                  {tab.usernames.length}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab header: title + add button */}
      <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-base font-semibold">{activeTab.label}</h3>
        {activeTab.canAdd && (
          <Button
            variant="primary"
            onClick={activeTab.onAddClick}
            disabled={activeTab.isMutating}
            className="px-3 py-2 text-xs"
          >
            + {activeTab.addLabel ?? `Add ${activeTab.label}`}
          </Button>
        )}
      </div>

      {/* Data table for the active tab */}
      <div className="mt-4">
        <MemberDataTable
          rows={activeTab.usernames}
          isLoading={activeTab.isLoading}
          selected={activeTab.selected}
          onSelect={activeTab.onSelect}
          onSelectAll={activeTab.onSelectAll}
          onRemove={activeTab.onRemove}
          onRemoveSelected={activeTab.onRemoveSelected}
          canRemove={activeTab.canRemove}
          removeLabel={
            activeTab.removeLabel ?? activeTab.label.replace(/s$/, "")
          }
          isMutating={activeTab.isMutating}
          currentUser={currentUser}
        />
      </div>
    </Card>
  );
}
