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
import { useTerm } from "@hooks/course";

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

  // The term reports which membership lists this user may see. Fetching a list
  // without the matching permission answers 403, so these flags gate the
  // requests rather than just hiding the results.
  const { data: term, isLoading: termLoading } = useTerm(courseId, termId);
  const membership = term?.capabilities.membership;

  const { data: students, isLoading: studentsLoading } = useStudents(
    courseId,
    termId,
    membership?.viewStudents ?? false,
  );
  const { data: teachingAssistants, isLoading: teachingAssistantsLoading } =
    useTeachingAssistants(
      courseId,
      termId,
      membership?.viewTeachingAssistants ?? false,
    );
  const { data: instructors, isLoading: instructorsLoading } = useInstructors(
    courseId,
    termId,
    membership?.viewInstructors ?? false,
  );
  const { data: observers, isLoading: observersLoading } = useObservers(
    courseId,
    termId,
    membership?.viewObservers ?? false,
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
      canView: membership?.viewStudents ?? false,
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
      canView: membership?.viewTeachingAssistants ?? false,
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
      canView: membership?.viewInstructors ?? false,
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
      canView: membership?.viewObservers ?? false,
      canManage: observers?.capabilities?.manage ?? false,
    },
  ].filter((role) => role.canView);

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

  if (termLoading) return <p className="text-gray-500">Loading…</p>;

  if (roles.length === 0) {
    return (
      <p className="text-gray-500">
        You are not allowed to view the members of this term.
      </p>
    );
  }

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
          {roles.map(({ id, label, data }) => (
            <div
              key={id}
              className="flex justify-between py-3 border-b border-gray-100 last:border-b-0"
            >
              <span className="text-gray-600">{label}</span>
              <strong>{data?.length ?? "—"}</strong>
            </div>
          ))}
        </Card>
      </div>
    </div>
  );
}
