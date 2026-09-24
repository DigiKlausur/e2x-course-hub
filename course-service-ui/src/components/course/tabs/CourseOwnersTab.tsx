import { useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import { Card, CardTitle } from "@components/ui/Card";
import { Button } from "@components/ui/Button";
import { AddMembersDialog } from "@components/membership/AddMembersDialog";
import { MemberDataTableWithCurrentUser } from "@components/membership/MemberDataTableWithCurrentUser";
import { useCourseOwners, useUpdateCourseOwners } from "@hooks/membership";
import { useCourse } from "@hooks/course";
import { Alert } from "@components/ui/Alert";
import { getErrorMessage } from "@/lib/errorMessage";

interface Props {
  courseId: string;
}

function toggleSelection(
  setSelection: Dispatch<SetStateAction<Set<string>>>,
  username: string,
) {
  setSelection((prev) => {
    const next = new Set(prev);
    if (next.has(username)) {
      next.delete(username);
    } else {
      next.add(username);
    }
    return next;
  });
}

function toggleSelectionForRows(
  setSelection: Dispatch<SetStateAction<Set<string>>>,
  select: boolean,
  usernames: string[],
) {
  setSelection((prev) => {
    const next = new Set(prev);
    if (select) {
      usernames.forEach((u) => next.add(u));
    } else {
      usernames.forEach((u) => next.delete(u));
    }
    return next;
  });
}

export function CourseOwnersTab({ courseId }: Props) {
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [selected, setSelected] = useState<Set<string>>(new Set());

  // Listing owners is permission guarded and answers 403, so the course's own
  // capability decides whether the request is made at all.
  const { data: course, isLoading: courseLoading } = useCourse(courseId);
  const owners = course?.capabilities.courseOwners;
  const canView = owners?.view ?? false;
  const canAdd = owners?.add ?? false;
  const canRemove = owners?.remove ?? false;

  const { data, isLoading } = useCourseOwners(courseId, canView);
  const update = useUpdateCourseOwners(courseId);

  const usernames = data?.usernames ?? [];

  if (courseLoading) return <p className="text-gray-500">Loading…</p>;

  if (!canView) {
    return (
      <p className="text-gray-500">
        You are not allowed to view the owners of this course.
      </p>
    );
  }

  return (
    <div className="max-w-2xl">
      <AddMembersDialog
        open={addDialogOpen}
        roleLabel="Owner"
        onCancel={() => setAddDialogOpen(false)}
        onConfirm={(names) => {
          update.mutate({ add: names });
          setAddDialogOpen(false);
        }}
      />
      <Card>
        {update.error && (
          <Alert className="mb-4" title="Could not update the owners">
            {getErrorMessage(update.error)}
          </Alert>
        )}
        <div className="flex items-center justify-between mb-4">
          <CardTitle>Course Owners</CardTitle>
          {canAdd && (
            <Button
              variant="primary"
              onClick={() => setAddDialogOpen(true)}
              disabled={update.isPending}
              className="px-3 py-2 text-xs"
            >
              + Add Owner
            </Button>
          )}
        </div>
        <MemberDataTableWithCurrentUser
          rows={usernames}
          isLoading={isLoading}
          selected={selected}
          onSelect={(username) => toggleSelection(setSelected, username)}
          onSelectAll={(select, rows) =>
            toggleSelectionForRows(setSelected, select, rows)
          }
          onRemove={(username) =>
            update.mutate(
              { remove: [username] },
              {
                onSuccess: () =>
                  setSelected((prev) => {
                    const next = new Set(prev);
                    next.delete(username);
                    return next;
                  }),
              },
            )
          }
          onRemoveSelected={() => {
            if (selected.size === 0) return;
            update.mutate(
              { remove: Array.from(selected) },
              { onSuccess: () => setSelected(new Set()) },
            );
          }}
          canRemove={canRemove}
          removeLabel="Owner"
          isMutating={update.isPending}
        />
      </Card>
    </div>
  );
}
