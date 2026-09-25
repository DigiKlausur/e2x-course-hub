import { useState } from "react";
import { Button } from "@components/ui/Button";
import { ConfirmDialog } from "@components/ui/ConfirmDialog";
import { DataTable } from "@components/ui/DataTable";
import type { DataTableColumn } from "@components/ui/DataTable";
import type { CurrentUser } from "@/api/types";
import { memberListActionText } from "@domain/actions";

const PAGE_SIZE_KEY = "member-table-page-size";

type RemoveDialog =
  | { type: "single"; username: string }
  | { type: "multiple"; count: number }
  | null;

function getDialogTitle(dialog: RemoveDialog, removeLabel: string): string {
  if (dialog?.type === "multiple") return `Remove Selected ${removeLabel}s`;
  return `Remove ${removeLabel}`;
}

function getDialogMessage(
  dialog: RemoveDialog,
  removeLabel: string,
  currentUser: CurrentUser,
  selected: Set<string>,
): string {
  if (dialog?.type === "single") {
    if (dialog.username === currentUser.username) {
      return "You are about to remove yourself. This action cannot be undone.";
    }
    return `Are you sure you want to remove ${dialog.username}?`;
  }
  if (dialog?.type === "multiple") {
    if (selected.has(currentUser.username)) {
      return `You are about to remove yourself along with ${dialog.count - 1} other ${removeLabel}s. This action cannot be undone.`;
    }
    return `Are you sure you want to remove these ${dialog.count} ${removeLabel}s?`;
  }
  return "";
}

function getRequireConfirmText(
  dialog: RemoveDialog,
  currentUser: CurrentUser,
  selected: Set<string>,
): string | undefined {
  const removingSelf =
    (dialog?.type === "single" && dialog.username === currentUser.username) ||
    (dialog?.type === "multiple" && selected.has(currentUser.username));
  return removingSelf ? currentUser.username : undefined;
}

export interface MemberDataTableProps {
  rows: string[];
  currentUser: CurrentUser;
  isLoading?: boolean;
  selected: Set<string>;
  onSelect: (username: string) => void;
  onSelectAll: (select: boolean, rows: string[]) => void;
  onRemove: (username: string) => void;
  onRemoveSelected: () => void;
  canRemove?: boolean;
  /** Singular label for the member type, e.g. "Student". Used in button labels and confirmations. */
  removeLabel?: string;
  isMutating?: boolean;
}

export function MemberDataTable({
  rows,
  currentUser,
  isLoading,
  selected,
  onSelect,
  onSelectAll,
  onRemove,
  onRemoveSelected,
  canRemove,
  removeLabel = "Member",
  isMutating,
}: MemberDataTableProps) {
  const [removeDialog, setRemoveDialog] = useState<RemoveDialog>(null);
  const removeText = memberListActionText.remove({
    singular: removeLabel,
    plural: `${removeLabel}s`,
  });

  const columns: DataTableColumn<string>[] = [
    {
      id: "username",
      header: "Username",
      cell: (username) => username,
      sortAccessor: (username) => username.toLowerCase(),
    },
    ...(canRemove
      ? [
          {
            id: "actions",
            header: "Actions",
            headerClassName: "w-36",
            cell: (username: string) => (
              <Button
                variant="danger"
                onClick={() => setRemoveDialog({ type: "single", username })}
                disabled={isMutating}
                className="px-3 py-1.5 text-xs whitespace-nowrap"
                title={removeText.description}
              >
                {removeText.label}
              </Button>
            ),
          },
        ]
      : []),
  ];

  const confirmRemove = () => {
    if (removeDialog?.type === "single") onRemove(removeDialog.username);
    else if (removeDialog?.type === "multiple") onRemoveSelected();
    setRemoveDialog(null);
  };

  return (
    <div>
      <DataTable
        rows={rows}
        getRowId={(username) => username}
        columns={columns}
        pageSizeStorageKey={PAGE_SIZE_KEY}
        isLoading={isLoading}
        loadingMessage="Loading members…"
        emptyMessage="No members yet."
        noMatchMessage="No matching usernames."
        filter={{
          placeholder: `Filter ${removeLabel.toLowerCase()}s...`,
          predicate: (username, query) =>
            username.toLowerCase().includes(query),
        }}
        selection={
          canRemove
            ? { selected, onToggle: onSelect, onToggleAll: onSelectAll }
            : undefined
        }
        renderSelectionBar={({ selectedCount }) => (
          <div className="mt-3 flex items-center justify-between rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-sm">
            <span>
              <strong>{selectedCount}</strong> selected
            </span>
            <Button
              variant="danger"
              onClick={() =>
                setRemoveDialog({ type: "multiple", count: selectedCount })
              }
              disabled={isMutating}
              className="px-3 py-1.5 text-xs"
            >
              Remove Selected {removeLabel}s
            </Button>
          </div>
        )}
      />

      {/* Confirmation dialog */}
      <ConfirmDialog
        open={removeDialog !== null}
        onClose={() => setRemoveDialog(null)}
        title={getDialogTitle(removeDialog, removeLabel)}
        message={getDialogMessage(
          removeDialog,
          removeLabel,
          currentUser,
          selected,
        )}
        requireConfirmationText={getRequireConfirmText(
          removeDialog,
          currentUser,
          selected,
        )}
        confirmText="Remove"
        cancelText="Cancel"
        onConfirm={confirmRemove}
        variant="destructive"
      />
    </div>
  );
}
