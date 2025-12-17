import { type ReactNode, useState } from "react";
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableFooter,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface DataTableProps<TData> {
  data: TData[];
  columns: ColumnDef<TData>[];
  searchValue?: string;
  onSearchChange?: (value: string) => void;
  emptyMessage?: string;
  emptyFilteredMessage?: string;
  pageSize?: number;
  initialSorting?: SortingState;
  showPagination?: boolean;
  showFooter?: boolean;
  footerContent?: (table: ReturnType<typeof useReactTable<TData>>) => ReactNode;
  className?: string;
}

export function DataTable<TData>({
  data,
  columns,
  searchValue = "",
  onSearchChange,
  emptyMessage = "No data available",
  emptyFilteredMessage = "No results found matching your search",
  pageSize = 20,
  initialSorting = [],
  showPagination = true,
  showFooter = false,
  footerContent,
  className,
}: DataTableProps<TData>) {
  const [sorting, setSorting] = useState<SortingState>(initialSorting);
  const [globalFilter, setGlobalFilter] = useState(searchValue);

  // Sync external search with internal state
  const handleGlobalFilterChange = (value: string) => {
    setGlobalFilter(value);
    onSearchChange?.(value);
  };

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      globalFilter,
    },
    onSortingChange: setSorting,
    onGlobalFilterChange: handleGlobalFilterChange,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: {
        pageSize,
      },
      sorting: initialSorting,
    },
  });

  const hasMultiplePages = table.getPageCount() > 1;
  const hasData = table.getRowModel().rows.length > 0;

  return (
    <div className={cn("space-y-4", className)}>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead
                    key={header.id}
                    onClick={header.column.getToggleSortingHandler()}
                    className={cn(
                      header.column.getCanSort() &&
                        "cursor-pointer select-none hover:bg-muted/80",
                    )}
                  >
                    {header.isPlaceholder ? null : (
                      <div className="flex items-center gap-1">
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext(),
                        )}
                        {header.column.getIsSorted() && (
                          <span className="text-primary text-xs">
                            {header.column.getIsSorted() === "asc"
                              ? " ▲"
                              : " ▼"}
                          </span>
                        )}
                      </div>
                    )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {!hasData ? (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center text-muted-foreground"
                >
                  {globalFilter ? emptyFilteredMessage : emptyMessage}
                </TableCell>
              </TableRow>
            ) : (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
          {showFooter && footerContent && (
            <TableFooter>
              <TableRow>
                <TableCell colSpan={columns.length}>
                  {footerContent(table)}
                </TableCell>
              </TableRow>
            </TableFooter>
          )}
        </Table>
      </div>

      {showPagination && hasMultiplePages && (
        <div className="flex justify-between items-center">
          <div className="text-sm text-muted-foreground">
            Page {table.getState().pagination.pageIndex + 1} of{" "}
            {table.getPageCount()}
          </div>
          <div className="flex items-center gap-2">
            <Button
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              size="sm"
              variant="outline"
            >
              Previous
            </Button>
            <Button
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              size="sm"
              variant="outline"
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
