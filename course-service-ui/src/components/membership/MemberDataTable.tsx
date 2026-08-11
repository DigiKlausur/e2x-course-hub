import { useMemo, useState } from "react";
import { Button } from "@components/ui/Button";
import { ConfirmDialog } from "@components/ui/ConfirmDialog";
import type { CurrentUser } from "@/api/types";

const PAGE_SIZE_KEY = "member-table-page-size";
const PAGE_SIZE_OPTIONS = [10, 25, 50, 100, 1000] as const;
type PageSize = (typeof PAGE_SIZE_OPTIONS)[number];

type RemoveDialog =
  | { type: "single"; username: string }
  | { type: "multiple"; count: number }
  | null;

function readStoredPageSize(): PageSize {
  try {
    const stored = localStorage.getItem(PAGE_SIZE_KEY);
    const parsed = Number(stored);
    return (PAGE_SIZE_OPTIONS as readonly number[]).includes(parsed)
      ? (parsed as PageSize)
      : 25;
  } catch {
    return 25;
  }
}

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
  const [filter, setFilter] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState<PageSize>(readStoredPageSize);
  const [removeDialog, setRemoveDialog] = useState<RemoveDialog>(null);

  const filterText = filter.trim().toLowerCase();

  const filteredRows = useMemo(() => {
    if (!filterText) return rows;
    return rows.filter((u) => u.toLowerCase().includes(filterText));
  }, [rows, filterText]);

  const pageCount = Math.max(1, Math.ceil(filteredRows.length / pageSize));
  const safePage = Math.min(page, pageCount);
  const startIndex = (safePage - 1) * pageSize;
  const visibleRows = filteredRows.slice(startIndex, startIndex + pageSize);

  const allVisibleSelected =
    visibleRows.length > 0 && visibleRows.every((u) => selected.has(u));
  const selectionCount = selected.size;

  const colSpan = canRemove ? 3 : 1;

  const paginationText =
    filteredRows.length === 0
      ? "No results"
      : `Showing ${startIndex + 1}–${Math.min(startIndex + pageSize, filteredRows.length)} of ${filteredRows.length}`;

  let tableBody: React.ReactNode;
  if (isLoading) {
    tableBody = (
      <tr>
        <td colSpan={colSpan} className="px-3 py-4 text-sm text-gray-500">
          Loading members…
        </td>
      </tr>
    );
  } else if (visibleRows.length === 0) {
    const emptyMessage =
      filteredRows.length === 0 && filterText
        ? "No matching usernames."
        : "No members yet.";
    tableBody = (
      <tr>
        <td colSpan={colSpan} className="px-3 py-4 text-sm text-gray-500">
          {emptyMessage}
        </td>
      </tr>
    );
  } else {
    tableBody = visibleRows.map((username) => {
      const isSelected = selected.has(username);
      return (
        <tr
          key={username}
          className={isSelected ? "bg-blue-50" : "hover:bg-gray-50"}
        >
          {canRemove && (
            <td className="border-t border-gray-200 px-3 py-2.5">
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => onSelect(username)}
                aria-label={`Select ${username}`}
              />
            </td>
          )}
          <td className="border-t border-gray-200 px-3 py-2.5 text-sm">
            {username}
          </td>
          {canRemove && (
            <td className="border-t border-gray-200 px-3 py-2.5">
              <Button
                variant="danger"
                onClick={() => setRemoveDialog({ type: "single", username })}
                disabled={isMutating}
                className="px-3 py-1.5 text-xs whitespace-nowrap"
              >
                Remove {removeLabel}
              </Button>
            </td>
          )}
        </tr>
      );
    });
  }

  const handlePageSizeChange = (size: PageSize) => {
    setPageSize(size);
    setPage(1);
    try {
      localStorage.setItem(PAGE_SIZE_KEY, String(size));
    } catch {
      // localStorage unavailable (e.g. private browsing restrictions)
    }
  };

  const confirmRemove = () => {
    if (removeDialog?.type === "single") onRemove(removeDialog.username);
    else if (removeDialog?.type === "multiple") onRemoveSelected();
    setRemoveDialog(null);
  };

  return (
    <div>
      {/* Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <input
          type="search"
          value={filter}
          onChange={(e) => {
            setFilter(e.target.value);
            setPage(1);
          }}
          placeholder={`Filter ${removeLabel.toLowerCase()}s...`}
          className="w-56 rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-hbrs-dark-blue focus:outline-none"
        />
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <label htmlFor="page-size-select" className="whitespace-nowrap">
            Rows per page
          </label>
          <select
            id="page-size-select"
            value={pageSize}
            onChange={(e) =>
              handlePageSizeChange(Number(e.target.value) as PageSize)
            }
            className="rounded-lg border border-gray-200 px-2 py-1.5 text-sm focus:border-hbrs-dark-blue focus:outline-none"
          >
            {PAGE_SIZE_OPTIONS.map((size) => (
              <option key={size} value={size}>
                {size}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Bulk action bar */}
      {selectionCount > 0 && canRemove && (
        <div className="mt-3 flex items-center justify-between rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-sm">
          <span>
            <strong>{selectionCount}</strong> selected
          </span>
          <Button
            variant="danger"
            onClick={() =>
              setRemoveDialog({ type: "multiple", count: selectionCount })
            }
            disabled={isMutating}
            className="px-3 py-1.5 text-xs"
          >
            Remove Selected {removeLabel}s
          </Button>
        </div>
      )}

      {/* Table */}
      <div className="mt-3 overflow-x-auto rounded-lg border border-gray-200">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
              {canRemove && (
                <th className="w-10 px-3 py-2.5">
                  <input
                    type="checkbox"
                    checked={allVisibleSelected}
                    onChange={(e) => onSelectAll(e.target.checked, visibleRows)}
                    aria-label="Select all visible members"
                  />
                </th>
              )}
              <th className="px-3 py-2.5">Username</th>
              {canRemove && <th className="w-36 px-3 py-2.5">Actions</th>}
            </tr>
          </thead>
          <tbody>{tableBody}</tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="mt-3 flex flex-wrap items-center justify-between gap-3 text-sm text-gray-500">
        <span>{paginationText}</span>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            onClick={() => setPage((p) => p - 1)}
            disabled={safePage <= 1}
            className="px-3 py-1.5 text-xs"
          >
            Prev
          </Button>
          <span className="text-xs text-gray-600">
            {safePage} / {pageCount}
          </span>
          <Button
            variant="secondary"
            onClick={() => setPage((p) => p + 1)}
            disabled={safePage >= pageCount}
            className="px-3 py-1.5 text-xs"
          >
            Next
          </Button>
        </div>
      </div>

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
