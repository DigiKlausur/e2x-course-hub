import { useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import { Card, CardTitle } from "@components/ui/Card";
import { Button } from "@components/ui/Button";
import { AddMembersDialog } from "@components/membership/AddMembersDialog";
import { MemberDataTableWithCurrentUser } from "@components/membership/MemberDataTableWithCurrentUser";
import { useCourseOwners, useUpdateCourseOwners } from "@hooks/membership";

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

  const { data, isLoading } = useCourseOwners(courseId);
  const update = useUpdateCourseOwners(courseId);

  const usernames = data?.usernames ?? [];
  const canManage = data?.capabilities?.manage ?? false;

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
        <div className="flex items-center justify-between mb-4">
          <CardTitle>Course Owners</CardTitle>
          {canManage && (
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
          canRemove={canManage}
          removeLabel="Owner"
          isMutating={update.isPending}
        />
      </Card>
    </div>
  );
}
