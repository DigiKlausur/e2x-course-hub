import type { DataTableColumn } from "@components/ui/DataTable";
import { formatDateTime } from "@/lib/dateTime";

/**
 * A sortable "Created" column. Rows created before creation dates were
 * recorded show "Unknown" and sort as the oldest.
 */
export function createdAtColumn<T>(
  getCreatedAt: (row: T) => string | null | undefined,
): DataTableColumn<T> {
  return {
    id: "created_at",
    header: "Created",
    cell: (row) => {
      const createdAt = getCreatedAt(row);
      return (
        <span className="text-gray-500">
          {createdAt ? formatDateTime(createdAt) : "Unknown"}
        </span>
      );
    },
    sortAccessor: (row) => {
      const createdAt = getCreatedAt(row);
      return createdAt ? Date.parse(createdAt) : 0;
    },
  };
}
