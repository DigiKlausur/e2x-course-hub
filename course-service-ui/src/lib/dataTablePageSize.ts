export const DATA_TABLE_PAGE_SIZE_OPTIONS = [5, 10, 25, 50, 100, 1000] as const;
export type DataTablePageSize = (typeof DATA_TABLE_PAGE_SIZE_OPTIONS)[number];

/** Reads a page size previously stored under `storageKey`, falling back to 25. */
export function readStoredPageSize(storageKey: string): DataTablePageSize {
  try {
    const stored = localStorage.getItem(storageKey);
    const parsed = Number(stored);
    return (DATA_TABLE_PAGE_SIZE_OPTIONS as readonly number[]).includes(parsed)
      ? (parsed as DataTablePageSize)
      : 25;
  } catch {
    return 25;
  }
}
