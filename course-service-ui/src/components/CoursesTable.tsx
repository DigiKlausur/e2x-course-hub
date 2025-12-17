import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { type ColumnDef, type Row } from "@tanstack/react-table";
import { useCourses } from "../hooks";
import type { Course } from "../types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { DataTable, DataTableWrapper } from "./common";

const CoursesTable = () => {
  const navigate = useNavigate();
  const { courses, loading, error, refresh } = useCourses();
  const [globalFilter, setGlobalFilter] = useState("");

  // Custom sorting function for term_id
  const sortTermId = (
    rowA: Row<Course>,
    rowB: Row<Course>,
    columnId: string,
  ) => {
    const a = rowA.getValue(columnId) as string;
    const b = rowB.getValue(columnId) as string;

    // Pattern for semester format like "WS24", "SS25"
    const semesterPattern = /^([A-Za-z]{2})(\d{2})$/;
    const matchA = a.match(semesterPattern);
    const matchB = b.match(semesterPattern);

    if (matchA && matchB) {
      const digitsA = matchA[2];
      const digitsB = matchB[2];
      const lettersA = matchA[1];
      const lettersB = matchB[1];

      const digitsCmp = digitsB.localeCompare(digitsA); // descending by default
      if (digitsCmp !== 0) return digitsCmp;
      return lettersB.localeCompare(lettersA); // descending
    }
    return b.localeCompare(a); // descending by default
  };

  // Define columns
  const columns = useMemo<ColumnDef<Course>[]>(
    () => [
      {
        accessorKey: "course_id",
        header: "Course ID",
        cell: (info) => info.getValue(),
      },
      {
        accessorKey: "course_name",
        header: "Name",
        cell: (info) => info.getValue(),
      },
      {
        accessorKey: "term_id",
        header: "Term",
        cell: (info) => info.getValue(),
        sortingFn: sortTermId,
      },
      {
        id: "actions",
        header: "Manage",
        cell: ({ row }) => (
          <Button
            onClick={() =>
              navigate(
                `/course/${row.original.course_id}/${row.original.term_id}`,
              )
            }
            size="sm"
            className="bg-hbrs-medium-blue text-white hover:bg-hbrs-medium-blue/90"
          >
            Manage
          </Button>
        ),
      },
    ],
    [navigate],
  );

  return (
    <DataTableWrapper
      loading={loading}
      error={error}
      onRetry={refresh}
      loadingMessage="Loading courses..."
      errorTitle="Error loading courses"
    >
      <div className="flex gap-2.5 mb-5 items-center">
        <Input
          type="text"
          placeholder="Search courses..."
          value={globalFilter}
          onChange={(e) => setGlobalFilter(e.target.value)}
          className="flex-1"
        />
        <Button onClick={refresh} variant="outline">
          Refresh
        </Button>
      </div>

      <DataTable
        data={courses}
        columns={columns}
        searchValue={globalFilter}
        onSearchChange={setGlobalFilter}
        emptyMessage="No courses available"
        emptyFilteredMessage="No courses found matching your search"
        pageSize={20}
        initialSorting={[
          { id: "course_id", desc: false },
          { id: "term_id", desc: true },
        ]}
      />
    </DataTableWrapper>
  );
};

export default CoursesTable;
