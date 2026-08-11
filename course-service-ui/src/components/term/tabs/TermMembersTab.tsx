import { useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import { Card, CardTitle } from "@components/ui/Card";
import { AddMembersDialog } from "@components/membership/AddMembersDialog";
import { TabbedMemberDataTableWithCurrentUser } from "@components/membership/TabbedMemberDataTableWithCurrentUser";
import {
  useObservers,
  useStudents,
  useTeachingAssistants,
  useInstructors,
  useUpdateObservers,
  useUpdateStudents,
  useUpdateTeachingAssistants,
  useUpdateInstructors,
} from "@hooks/membership";

type DialogTarget =
  "students" | "teaching-assistants" | "instructors" | "observers";

interface Props {
  courseId: string;
  termId: string;
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

export function TermMembersTab({ courseId, termId }: Props) {
  const [addDialogFor, setAddDialogFor] = useState<DialogTarget | null>(null);

  const { data: students, isLoading: studentsLoading } = useStudents(
    courseId,
    termId,
  );
  const { data: teachingAssistants, isLoading: teachingAssistantsLoading } =
    useTeachingAssistants(courseId, termId);
  const { data: instructors, isLoading: instructorsLoading } = useInstructors(
    courseId,
    termId,
  );
  const { data: observers, isLoading: observersLoading } = useObservers(
    courseId,
    termId,
  );

  const [selectedStudents, setSelectedStudents] = useState<Set<string>>(
    new Set(),
  );
  const [selectedTeachingAssistants, setSelectedTeachingAssistants] = useState<
    Set<string>
  >(new Set());
  const [selectedInstructors, setSelectedInstructors] = useState<Set<string>>(
    new Set(),
  );
  const [selectedObservers, setSelectedObservers] = useState<Set<string>>(
    new Set(),
  );

  const updateStudents = useUpdateStudents(courseId, termId);
  const updateTeachingAssistants = useUpdateTeachingAssistants(
    courseId,
    termId,
  );
  const updateInstructors = useUpdateInstructors(courseId, termId);
  const updateObservers = useUpdateObservers(courseId, termId);

  const roles = [
    {
      id: "students" as const,
      label: "Students",
      removeLabel: "Student",
      data: students?.usernames,
      isLoading: studentsLoading,
      selected: selectedStudents,
      setSelected: setSelectedStudents,
      update: updateStudents,
      canManage: students?.capabilities?.manage ?? false,
    },
    {
      id: "teaching-assistants" as const,
      label: "Teaching Assistants",
      removeLabel: "Teaching Assistant",
      data: teachingAssistants?.usernames,
      isLoading: teachingAssistantsLoading,
      selected: selectedTeachingAssistants,
      setSelected: setSelectedTeachingAssistants,
      update: updateTeachingAssistants,
      canManage: teachingAssistants?.capabilities?.manage ?? false,
    },
    {
      id: "instructors" as const,
      label: "Instructors",
      removeLabel: "Instructor",
      data: instructors?.usernames,
      isLoading: instructorsLoading,
      selected: selectedInstructors,
      setSelected: setSelectedInstructors,
      update: updateInstructors,
      canManage: instructors?.capabilities?.manage ?? false,
    },
    {
      id: "observers" as const,
      label: "Observers",
      removeLabel: "Observer",
      data: observers?.usernames,
      isLoading: observersLoading,
      selected: selectedObservers,
      setSelected: setSelectedObservers,
      update: updateObservers,
      canManage: observers?.capabilities?.manage ?? false,
    },
  ];

  const activeRole = roles.find((r) => r.id === addDialogFor);

  const handleDialogConfirm = (usernames: string[]) => {
    activeRole?.update.mutate({ add: usernames });
    setAddDialogFor(null);
  };

  const tabs = roles.map(
    ({
      id,
      label,
      removeLabel,
      data,
      isLoading,
      selected,
      setSelected,
      update,
      canManage,
    }) => ({
      id,
      label,
      usernames: data ?? [],
      isLoading,
      selected,
      onSelect: (username: string) => toggleSelection(setSelected, username),
      onSelectAll: (select: boolean, usernames: string[]) =>
        toggleSelectionForRows(setSelected, select, usernames),
      onRemove: (username: string) => {
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
        );
      },
      onRemoveSelected: () => {
        if (selected.size === 0) return;
        update.mutate(
          { remove: Array.from(selected) },
          { onSuccess: () => setSelected(new Set()) },
        );
      },
      canAdd: canManage,
      addLabel: `Add ${label}`,
      onAddClick: () => setAddDialogFor(id),
      canRemove: canManage,
      removeLabel,
      isMutating: update.isPending,
    }),
  );

  return (
    <div className="grid grid-cols-[2fr_1fr] gap-6">
      <AddMembersDialog
        open={addDialogFor !== null}
        roleLabel={activeRole?.label ?? "Unknown"}
        onCancel={() => setAddDialogFor(null)}
        onConfirm={handleDialogConfirm}
      />
      <div>
        <TabbedMemberDataTableWithCurrentUser tabs={tabs} />
      </div>

      <div>
        <Card>
          <CardTitle>Summary</CardTitle>
          <div className="flex justify-between py-3 border-b border-gray-100">
            <span className="text-gray-600">Students</span>
            <strong>{students?.usernames.length ?? "—"}</strong>
          </div>
          <div className="flex justify-between py-3 border-b border-gray-100">
            <span className="text-gray-600">Teaching Assistants</span>
            <strong>{teachingAssistants?.usernames.length ?? "—"}</strong>
          </div>
          <div className="flex justify-between py-3">
            <span className="text-gray-600">Instructors</span>
            <strong>{instructors?.usernames.length ?? "—"}</strong>
          </div>
          <div className="flex justify-between py-3">
            <span className="text-gray-600">Observers</span>
            <strong>{observers?.usernames.length ?? "—"}</strong>
          </div>
        </Card>
      </div>
    </div>
  );
}
