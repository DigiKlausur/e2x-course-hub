import { useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import { Card, CardTitle } from "@components/ui/Card";
import { Row } from "@components/ui/Row";
import { Alert } from "@components/ui/Alert";
import { RuntimeConfigEditor } from "@components/infrastructure/RuntimeConfigEditor";
import { AddMembersDialog } from "@components/membership/AddMembersDialog";
import { TabbedMemberDataTableWithCurrentUser } from "@components/membership/TabbedMemberDataTableWithCurrentUser";
import { useTerm, useUpdateTermEnvironment } from "@hooks/course";
import { useImageCatalog, useResourceCatalog } from "@hooks/catalog";
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
import { getErrorMessage } from "@/lib/errorMessage";
import { MembershipRole, memberLabels } from "@domain/roles";
import {
  membershipCapabilityText,
  termCapabilityText,
} from "@domain/capabilities";
import type { ImageSelection, SpawnRole } from "@api/types";

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

export function TermOverviewTab({ courseId, termId }: Props) {
  const [addDialogFor, setAddDialogFor] = useState<DialogTarget | null>(null);

  // The term reports which membership lists this user may see and change.
  // Fetching a list without the matching permission answers 403, so the view
  // flags gate the requests rather than just hiding the results.
  const { data: term, isLoading: termLoading } = useTerm(courseId, termId);
  const membership = term?.capabilities.membership;

  const { data: imageCatalog } = useImageCatalog();
  const { data: resourceCatalog } = useResourceCatalog();
  const updateEnvironment = useUpdateTermEnvironment(courseId, termId);

  const { data: students, isLoading: studentsLoading } = useStudents(
    courseId,
    termId,
    membership?.students.view ?? false,
  );
  const { data: teachingAssistants, isLoading: teachingAssistantsLoading } =
    useTeachingAssistants(
      courseId,
      termId,
      membership?.teachingAssistants.view ?? false,
    );
  const { data: instructors, isLoading: instructorsLoading } = useInstructors(
    courseId,
    termId,
    membership?.instructors.view ?? false,
  );
  const { data: observers, isLoading: observersLoading } = useObservers(
    courseId,
    termId,
    membership?.observers.view ?? false,
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
      labels: memberLabels[MembershipRole.Student],
      data: students?.usernames,
      isLoading: studentsLoading,
      selected: selectedStudents,
      setSelected: setSelectedStudents,
      update: updateStudents,
      canView: membership?.students.view ?? false,
      canAdd: membership?.students.add ?? false,
      canRemove: membership?.students.remove ?? false,
    },
    {
      id: "teaching-assistants" as const,
      labels: memberLabels[MembershipRole.TeachingAssistant],
      data: teachingAssistants?.usernames,
      isLoading: teachingAssistantsLoading,
      selected: selectedTeachingAssistants,
      setSelected: setSelectedTeachingAssistants,
      update: updateTeachingAssistants,
      canView: membership?.teachingAssistants.view ?? false,
      canAdd: membership?.teachingAssistants.add ?? false,
      canRemove: membership?.teachingAssistants.remove ?? false,
    },
    {
      id: "instructors" as const,
      labels: memberLabels[MembershipRole.Instructor],
      data: instructors?.usernames,
      isLoading: instructorsLoading,
      selected: selectedInstructors,
      setSelected: setSelectedInstructors,
      update: updateInstructors,
      canView: membership?.instructors.view ?? false,
      canAdd: membership?.instructors.add ?? false,
      canRemove: membership?.instructors.remove ?? false,
    },
    {
      id: "observers" as const,
      labels: memberLabels[MembershipRole.Observer],
      data: observers?.usernames,
      isLoading: observersLoading,
      selected: selectedObservers,
      setSelected: setSelectedObservers,
      update: updateObservers,
      canView: membership?.observers.view ?? false,
      canAdd: membership?.observers.add ?? false,
      canRemove: membership?.observers.remove ?? false,
    },
  ].filter((role) => role.canView);

  const activeRole = roles.find((r) => r.id === addDialogFor);
  // One banner for the whole tab: only one role can be mutated at a time, and
  // the failure belongs to whichever update was last attempted.
  const mutationError = roles.find((role) => role.update.error)?.update.error;

  const handleDialogConfirm = (usernames: string[]) => {
    activeRole?.update.mutate({ add: usernames });
    setAddDialogFor(null);
  };

  const memberTabs = roles.map(
    ({
      id,
      labels,
      data,
      isLoading,
      selected,
      setSelected,
      update,
      canAdd,
      canRemove,
    }) => ({
      id,
      label: labels.plural,
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
      canAdd,
      addLabel: membershipCapabilityText.add(labels).label,
      addDescription: membershipCapabilityText.add(labels).description,
      onAddClick: () => setAddDialogFor(id),
      canRemove,
      removeLabel: labels.singular,
      isMutating: update.isPending,
    }),
  );

  const handleImageConfirm = (selection: ImageSelection) => {
    updateEnvironment.mutate({ image: selection });
  };

  const handleResourceConfirm = (role: SpawnRole, tier: string) => {
    updateEnvironment.mutate({ resources: { [role]: tier } });
  };

  if (termLoading) return <p className="text-gray-500">Loading…</p>;

  return (
    <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-[2fr_1fr]">
      <div>
        <AddMembersDialog
          open={addDialogFor !== null}
          roleLabel={activeRole?.labels.plural ?? "Unknown"}
          onCancel={() => setAddDialogFor(null)}
          onConfirm={handleDialogConfirm}
        />

        {mutationError && (
          <Alert className="mb-4" title="Could not update the members">
            {getErrorMessage(mutationError)}
          </Alert>
        )}

        {roles.length === 0 ? (
          <p className="text-gray-500">
            You are not allowed to view the members of this term.
          </p>
        ) : (
          <TabbedMemberDataTableWithCurrentUser tabs={memberTabs} />
        )}
      </div>

      <div>
        <Card>
          <CardTitle>General Information</CardTitle>
          <Row label="Course">{courseId}</Row>
          <Row label="Term">{termId}</Row>
        </Card>

        <RuntimeConfigEditor
          title="Term Runtime"
          description={termCapabilityText.selectEnvironment.description}
          imageSelection={term?.environment.image}
          resourcesSelection={term?.environment.resources}
          imageCatalog={imageCatalog?.catalog}
          resourceCatalog={resourceCatalog?.catalog}
          canEdit={term?.capabilities.selectEnvironment ?? false}
          errorMessage={
            updateEnvironment.error
              ? getErrorMessage(updateEnvironment.error)
              : undefined
          }
          onImageConfirm={handleImageConfirm}
          onResourceConfirm={handleResourceConfirm}
        />
      </div>
    </div>
  );
}
