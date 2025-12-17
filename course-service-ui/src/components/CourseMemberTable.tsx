import {
  useState,
  forwardRef,
  useImperativeHandle,
  useMemo,
} from "react";
import { type ColumnDef } from "@tanstack/react-table";
import { useCourseMembers, useAssignableRoles, useMemberDelete } from "../hooks";
import type { CourseMember } from "../types";
import { cn } from "@/lib/utils";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import {
  ConfirmDialog,
  RemoveUserFromCourseDialog,
  RemoveSelfFromCourseDialog,
} from "./dialogs";
import { Input } from "./ui/input";
import { DataTable, DataTableWrapper } from "./common";

interface CourseMemberTableProps {
  courseId: string;
  termId: string;
  onAddMembers?: (role: string) => void;
}

export interface CourseMemberTableRef {
  refresh: () => void;
}

const CourseMemberTable = forwardRef<
  CourseMemberTableRef,
  CourseMemberTableProps
>(({ courseId, termId, onAddMembers }, ref) => {
  const { members, loading, error, refresh } = useCourseMembers({
    courseId,
    termId,
  });
  const { assignableRoles } = useAssignableRoles(courseId, termId);
  const {
    deletingUser,
    deleteError,
    confirmDialog,
    initiateDelete,
    confirmDelete,
    cancelDelete,
    clearError,
  } = useMemberDelete({ courseId, termId, onSuccess: refresh });

  const [globalFilter, setGlobalFilter] = useState("");

  // Expose refresh method to parent via ref
  useImperativeHandle(ref, () => ({
    refresh,
  }));

  // Define columns
  const columns = useMemo<ColumnDef<CourseMember>[]>(
    () => [
      {
        accessorKey: "username",
        header: "Username",
        cell: (info) => info.getValue(),
      },
      {
        accessorKey: "role",
        header: "Role",
        cell: (info) => {
          const role = (info.getValue() as string).toLowerCase();
          const variant =
            role === "instructor"
              ? "default"
              : role === "student"
                ? "secondary"
                : "outline";

          return (
            <Badge
              variant={variant}
              className={cn(
                role === "instructor" &&
                  "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
                role === "student" &&
                  "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
                role === "grader" &&
                  "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
              )}
            >
              {info.getValue() as string}
            </Badge>
          );
        },
      },
      {
        id: "actions",
        header: "Actions",
        cell: ({ row }) => {
          const member = row.original;
          return member.deletable !== false ? (
            <Button
              variant="destructive"
              size="sm"
              onClick={() => initiateDelete(member.username)}
              disabled={deletingUser === member.username}
            >
              {deletingUser === member.username ? "Removing..." : "Remove"}
            </Button>
          ) : (
            <span className="text-muted-foreground">-</span>
          );
        },
      },
    ],
    [deletingUser, initiateDelete],
  );

  return (
    <DataTableWrapper
      loading={loading}
      error={error}
      onRetry={refresh}
      loadingMessage="Loading course members..."
      errorTitle="Error loading course members"
    >
      <div>
        <div className="flex flex-col gap-5 mb-5 md:flex-row md:items-center md:justify-between">
          <h2 className="text-2xl font-bold m-0">Course Members</h2>
          <div className="flex gap-2.5 items-center flex-wrap">
            <Input
              type="text"
              placeholder="Search members..."
              value={globalFilter}
              onChange={(e) => setGlobalFilter(e.target.value)}
              className="w-48"
            />
            <Button onClick={refresh} variant="outline">
              Refresh
            </Button>
            {onAddMembers &&
              assignableRoles.map((role) => {
                return (
                  <Button key={role} onClick={() => onAddMembers(role)}>
                    Add {role.charAt(0).toUpperCase() + role.slice(1)}s
                  </Button>
                );
              })}
          </div>
        </div>

        <DataTable
          data={members}
          columns={columns}
          searchValue={globalFilter}
          onSearchChange={setGlobalFilter}
          emptyMessage="No members in this course"
          emptyFilteredMessage="No members found matching your search"
          pageSize={20}
          showFooter={true}
          footerContent={(table) => (
            <div className="flex justify-between items-center">
              <div className="text-sm text-muted-foreground">
                Showing {table.getRowModel().rows.length} of{" "}
                {table.getFilteredRowModel().rows.length} member(s)
                {globalFilter && ` (filtered from ${members.length} total)`}
              </div>
            </div>
          )}
        />

        {/* Delete Error Dialog */}
        {deleteError && (
          <ConfirmDialog
            title="Error Removing User"
            message={`Failed to remove user: ${deleteError}`}
            confirmText="OK"
            onConfirm={clearError}
            onCancel={clearError}
          />
        )}

        {/* Confirmation Dialogs */}
        {confirmDialog && !confirmDialog.isCurrentUser && (
          <RemoveUserFromCourseDialog
            userName={confirmDialog ? confirmDialog.username : ""}
            onConfirm={() => confirmDelete()}
            onCancel={cancelDelete}
          />
        )}

        {confirmDialog && confirmDialog.isCurrentUser && (
          <RemoveSelfFromCourseDialog
            username={confirmDialog.username}
            onConfirm={() => confirmDelete(confirmDialog.username)}
            onCancel={cancelDelete}
          />
        )}
      </div>
    </DataTableWrapper>
  );
});

CourseMemberTable.displayName = "CourseMemberTable";

export default CourseMemberTable;
