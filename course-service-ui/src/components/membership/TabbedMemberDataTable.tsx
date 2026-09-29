import { useMemo, useState } from "react";

import { Button } from "@components/ui/Button";
import { Card } from "@components/ui/Card";
import { Tabs } from "@components/ui/Tabs";
import { MemberDataTable } from "./MemberDataTable";
import { RoleInfoLink } from "@components/actions/RoleInfoLink";
import type { RoleContext } from "@components/actions/RoleActionsModal";
import type { MembershipRole } from "@domain/roles";
import type { CurrentUser } from "@api/types";

export interface MemberTabConfig {
  id: string;
  label: string;
  /** Offers the explanation of the role next to the tab's title. */
  role?: MembershipRole;
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
  addDescription?: string;
  onAddClick?: () => void;
  isMutating?: boolean;
}

export interface TabbedMemberDataTableProps {
  tabs: MemberTabConfig[];
  currentUser: CurrentUser;
  /** The course and semester of the lists, named in the explanation of a role. */
  roleContext?: RoleContext;
}

export function TabbedMemberDataTable({
  tabs,
  currentUser,
  roleContext,
}: TabbedMemberDataTableProps) {
  const [activeTabId, setActiveTabId] = useState<string>(tabs[0]?.id ?? "");

  const activeTab = useMemo(
    () => tabs.find((tab) => tab.id === activeTabId) ?? tabs[0],
    [tabs, activeTabId],
  );

  if (!activeTab) return null;

  return (
    <Card className="mb-0">
      <Tabs
        tabs={tabs.map((tab) => ({
          id: tab.id,
          label: tab.label,
          badge: tab.usernames.length,
        }))}
        activeId={activeTab.id}
        onChange={setActiveTabId}
      />

      {/* Tab header: title + add button */}
      <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-baseline gap-4">
          <h3 className="text-base font-semibold">{activeTab.label}</h3>
          {activeTab.role && (
            <RoleInfoLink role={activeTab.role} context={roleContext} />
          )}
        </div>
        {activeTab.canAdd && (
          <Button
            variant="primary"
            onClick={activeTab.onAddClick}
            disabled={activeTab.isMutating}
            className="px-3 py-2 text-xs"
            title={activeTab.addDescription}
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
