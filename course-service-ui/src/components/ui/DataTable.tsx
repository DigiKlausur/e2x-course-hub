import type { ReactNode } from "react";
import { useMemo, useState } from "react";
import { Button } from "@components/ui/Button";
import {
  DATA_TABLE_PAGE_SIZE_OPTIONS,
  readStoredPageSize,
} from "@/lib/dataTablePageSize";
import type { DataTablePageSize } from "@/lib/dataTablePageSize";

export type DataTableSortDirection = "asc" | "desc";

export interface DataTableColumn<T> {
  id: string;
  header: ReactNode;
  cell: (row: T) => ReactNode;
  /** Enables sorting on this column by returning the value to compare rows by. */
  sortAccessor?: (row: T) => string | number;
  headerClassName?: string;
  cellClassName?: string;
}

export interface DataTableSelection<T> {
  selected: Set<string>;
  onToggle: (id: string) => void;
  onToggleAll: (select: boolean, rows: T[]) => void;
}

export interface DataTableFilter<T> {
  placeholder: string;
  predicate: (row: T, query: string) => boolean;
}

export interface DataTableProps<T> {
  rows: T[];
  getRowId: (row: T) => string;
  columns: DataTableColumn<T>[];
  /** localStorage key the chosen page size is persisted under. */
  pageSizeStorageKey: string;
  isLoading?: boolean;
  loadingMessage?: string;
  emptyMessage?: string;
  noMatchMessage?: string;
  filter?: DataTableFilter<T>;
  defaultSort?: { columnId: string; direction: DataTableSortDirection };
  selection?: DataTableSelection<T>;
  /** Rendered between the toolbar and the table, e.g. a bulk-action bar. */
  renderSelectionBar?: (params: { selectedCount: number }) => ReactNode;
  /** Extra control shown in the toolbar, next to the page size selector. */
  toolbarEnd?: ReactNode;
  rowClassName?: (row: T, isSelected: boolean) => string;
}

export function DataTable<T>({
  rows,
  getRowId,
  columns,
  pageSizeStorageKey,
  isLoading,
  loadingMessage = "Loading…",
  emptyMessage = "No results.",
  noMatchMessage = "No matching rows.",
  filter,
  defaultSort,
  selection,
  renderSelectionBar,
  toolbarEnd,
  rowClassName,
}: DataTableProps<T>) {
  const [filterText, setFilterText] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState<DataTablePageSize>(() =>
    readStoredPageSize(pageSizeStorageKey),
  );
  const [sort, setSort] = useState(defaultSort ?? null);

  const trimmedFilter = filterText.trim().toLowerCase();

  const filteredRows = useMemo(() => {
    if (!filter || !trimmedFilter) return rows;
    return rows.filter((row) => filter.predicate(row, trimmedFilter));
  }, [rows, filter, trimmedFilter]);

  const sortedRows = useMemo(() => {
    if (!sort) return filteredRows;
    const column = columns.find((c) => c.id === sort.columnId);
    const accessor = column?.sortAccessor;
    if (!accessor) return filteredRows;
    const sorted = [...filteredRows].sort((a, b) => {
      const av = accessor(a);
      const bv = accessor(b);
      if (av < bv) return -1;
      if (av > bv) return 1;
      return 0;
    });
    if (sort.direction === "desc") sorted.reverse();
    return sorted;
  }, [filteredRows, sort, columns]);

  const pageCount = Math.max(1, Math.ceil(sortedRows.length / pageSize));
  const safePage = Math.min(page, pageCount);
  const startIndex = (safePage - 1) * pageSize;
  const visibleRows = sortedRows.slice(startIndex, startIndex + pageSize);

  const selectedCount = selection?.selected.size ?? 0;
  const allVisibleSelected =
    !!selection &&
    visibleRows.length > 0 &&
    visibleRows.every((row) => selection.selected.has(getRowId(row)));

  const colSpan = columns.length + (selection ? 1 : 0);

  const paginationText =
    sortedRows.length === 0
      ? "No results"
      : `Showing ${startIndex + 1}–${Math.min(startIndex + pageSize, sortedRows.length)} of ${sortedRows.length}`;

  const handleFilterChange = (value: string) => {
    setFilterText(value);
    setPage(1);
  };

  const handlePageSizeChange = (size: DataTablePageSize) => {
    setPageSize(size);
    setPage(1);
    try {
      localStorage.setItem(pageSizeStorageKey, String(size));
    } catch {
      // localStorage unavailable (e.g. private browsing restrictions)
    }
  };

  const handleSortClick = (columnId: string) => {
    setSort((current) =>
      current?.columnId === columnId
        ? { columnId, direction: current.direction === "asc" ? "desc" : "asc" }
        : { columnId, direction: "asc" },
    );
  };

  let tableBody: ReactNode;
  if (isLoading) {
    tableBody = (
      <tr>
        <td colSpan={colSpan} className="px-3 py-4 text-sm text-gray-500">
          {loadingMessage}
        </td>
      </tr>
    );
  } else if (visibleRows.length === 0) {
    tableBody = (
      <tr>
        <td colSpan={colSpan} className="px-3 py-4 text-sm text-gray-500">
          {sortedRows.length === 0 && trimmedFilter
            ? noMatchMessage
            : emptyMessage}
        </td>
      </tr>
    );
  } else {
    tableBody = visibleRows.map((row) => {
      const id = getRowId(row);
      const isSelected = !!selection?.selected.has(id);
      return (
        <tr
          key={id}
          className={
            rowClassName?.(row, isSelected) ??
            (isSelected ? "bg-blue-50" : "hover:bg-gray-50")
          }
        >
          {selection && (
            <td className="border-t border-gray-200 px-3 py-2.5">
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => selection.onToggle(id)}
                aria-label={`Select row ${id}`}
              />
            </td>
          )}
          {columns.map((column) => (
            <td
              key={column.id}
              className={`border-t border-gray-200 px-3 py-2.5 text-sm ${column.cellClassName ?? ""}`}
            >
              {column.cell(row)}
            </td>
          ))}
        </tr>
      );
    });
  }

  return (
    <div>
      {/* Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        {filter ? (
          <input
            type="search"
            value={filterText}
            onChange={(e) => handleFilterChange(e.target.value)}
            placeholder={filter.placeholder}
            className="w-56 rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-hbrs-dark-blue focus:outline-none"
          />
        ) : (
          <div />
        )}
        <div className="flex items-center gap-3">
          {toolbarEnd}
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <label
              htmlFor={`${pageSizeStorageKey}-select`}
              className="whitespace-nowrap"
            >
              Rows per page
            </label>
            <select
              id={`${pageSizeStorageKey}-select`}
              value={pageSize}
              onChange={(e) =>
                handlePageSizeChange(
                  Number(e.target.value) as DataTablePageSize,
                )
              }
              className="rounded-lg border border-gray-200 px-2 py-1.5 text-sm focus:border-hbrs-dark-blue focus:outline-none"
            >
              {DATA_TABLE_PAGE_SIZE_OPTIONS.map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Selection bar */}
      {selection &&
        selectedCount > 0 &&
        renderSelectionBar?.({ selectedCount })}

      {/* Table */}
      <div className="mt-3 overflow-x-auto rounded-lg border border-gray-200">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
              {selection && (
                <th className="w-10 px-3 py-2.5">
                  <input
                    type="checkbox"
                    checked={allVisibleSelected}
                    onChange={(e) =>
                      selection.onToggleAll(e.target.checked, visibleRows)
                    }
                    aria-label="Select all visible rows"
                  />
                </th>
              )}
              {columns.map((column) => {
                const isSortable = !!column.sortAccessor;
                const isSorted = sort?.columnId === column.id;
                return (
                  <th
                    key={column.id}
                    className={`px-3 py-2.5 ${column.headerClassName ?? ""}`}
                  >
                    {isSortable ? (
                      <button
                        type="button"
                        onClick={() => handleSortClick(column.id)}
                        className="inline-flex items-center gap-1 uppercase tracking-wide text-gray-500 hover:text-gray-700"
                      >
                        {column.header}
                        <span className="text-[10px]">
                          {isSorted
                            ? sort.direction === "asc"
                              ? "▲"
                              : "▼"
                            : ""}
                        </span>
                      </button>
                    ) : (
                      column.header
                    )}
                  </th>
                );
              })}
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
    </div>
  );
}
