import { useState } from "react";
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
import { useSelection } from "@hooks/ui";
import { getErrorMessage } from "@/lib/errorMessage";
import { MembershipRole, memberLabels } from "@domain/roles";
import { memberListActionText, termActionText } from "@domain/actions";
import type { ImageSelection, SpawnRole } from "@api/types";

type DialogTarget =
  "students" | "teaching-assistants" | "instructors" | "observers";

interface Props {
  courseId: string;
  termId: string;
}

export function TermOverviewTab({ courseId, termId }: Props) {
  const [addDialogFor, setAddDialogFor] = useState<DialogTarget | null>(null);

  // The term reports which membership lists this user may see and change.
  // Fetching a list without the matching permission answers 403, so the view
  // flags gate the requests rather than just hiding the results.
  const { data: term, isLoading: termLoading } = useTerm(courseId, termId);
  const members = term?.actions.members;

  const { data: imageCatalog } = useImageCatalog();
  const { data: resourceCatalog } = useResourceCatalog();
  const updateEnvironment = useUpdateTermEnvironment(courseId, termId);

  const { data: students, isLoading: studentsLoading } = useStudents(
    courseId,
    termId,
    members?.students.list ?? false,
  );
  const { data: teachingAssistants, isLoading: teachingAssistantsLoading } =
    useTeachingAssistants(
      courseId,
      termId,
      members?.teachingAssistants.list ?? false,
    );
  const { data: instructors, isLoading: instructorsLoading } = useInstructors(
    courseId,
    termId,
    members?.instructors.list ?? false,
  );
  const { data: observers, isLoading: observersLoading } = useObservers(
    courseId,
    termId,
    members?.observers.list ?? false,
  );

  const studentSelection = useSelection();
  const teachingAssistantSelection = useSelection();
  const instructorSelection = useSelection();
  const observerSelection = useSelection();

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
      role: MembershipRole.Student,
      labels: memberLabels[MembershipRole.Student],
      data: students?.usernames,
      isLoading: studentsLoading,
      selection: studentSelection,
      update: updateStudents,
      canView: members?.students.list ?? false,
      canAdd: members?.students.add ?? false,
      canRemove: members?.students.remove ?? false,
    },
    {
      id: "teaching-assistants" as const,
      role: MembershipRole.TeachingAssistant,
      labels: memberLabels[MembershipRole.TeachingAssistant],
      data: teachingAssistants?.usernames,
      isLoading: teachingAssistantsLoading,
      selection: teachingAssistantSelection,
      update: updateTeachingAssistants,
      canView: members?.teachingAssistants.list ?? false,
      canAdd: members?.teachingAssistants.add ?? false,
      canRemove: members?.teachingAssistants.remove ?? false,
    },
    {
      id: "instructors" as const,
      role: MembershipRole.Instructor,
      labels: memberLabels[MembershipRole.Instructor],
      data: instructors?.usernames,
      isLoading: instructorsLoading,
      selection: instructorSelection,
      update: updateInstructors,
      canView: members?.instructors.list ?? false,
      canAdd: members?.instructors.add ?? false,
      canRemove: members?.instructors.remove ?? false,
    },
    {
      id: "observers" as const,
      role: MembershipRole.Observer,
      labels: memberLabels[MembershipRole.Observer],
      data: observers?.usernames,
      isLoading: observersLoading,
      selection: observerSelection,
      update: updateObservers,
      canView: members?.observers.list ?? false,
      canAdd: members?.observers.add ?? false,
      canRemove: members?.observers.remove ?? false,
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
      role,
      labels,
      data,
      isLoading,
      selection,
      update,
      canAdd,
      canRemove,
    }) => ({
      id,
      role,
      label: labels.plural,
      usernames: data ?? [],
      isLoading,
      selected: selection.selected,
      onSelect: selection.toggle,
      onSelectAll: selection.toggleRows,
      onRemove: (username: string) => {
        update.mutate(
          { remove: [username] },
          { onSuccess: () => selection.remove(username) },
        );
      },
      onRemoveSelected: () => {
        if (selection.selected.size === 0) return;
        update.mutate(
          { remove: Array.from(selection.selected) },
          { onSuccess: selection.clear },
        );
      },
      canAdd,
      addLabel: memberListActionText.add(labels).label,
      addDescription: memberListActionText.add(labels).description,
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
          role={activeRole?.role}
          roleContext={{ courseId, termId }}
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
            You are not allowed to view the members of this semester.
          </p>
        ) : (
          <TabbedMemberDataTableWithCurrentUser
            tabs={memberTabs}
            roleContext={{ courseId, termId }}
          />
        )}
      </div>

      <div>
        <Card>
          <CardTitle>General Information</CardTitle>
          <Row label="Course">{courseId}</Row>
          <Row label="Semester">{termId}</Row>
        </Card>

        <RuntimeConfigEditor
          title="Semester Runtime"
          description={termActionText.environment.select.description}
          imageSelection={term?.environment.image}
          resourcesSelection={term?.environment.resources}
          imageCatalog={imageCatalog?.catalog}
          resourceCatalog={resourceCatalog?.catalog}
          canEdit={term?.actions.environment.select ?? false}
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
