import { useState } from "react";
import type { UseMutationResult } from "@tanstack/react-query";
import { useSelection } from "@hooks/ui";
import { Card, CardTitle } from "@components/ui/Card";
import { Button } from "@components/ui/Button";
import { Alert } from "@components/ui/Alert";
import { AddMembersDialog } from "@components/membership/AddMembersDialog";
import { MemberDataTableWithCurrentUser } from "@components/membership/MemberDataTableWithCurrentUser";
import { getErrorMessage } from "@/lib/errorMessage";
import { memberListActionText } from "@domain/actions";
import type { MemberLabels } from "@domain/roles";
import type { MemberListActions, MembershipPatch } from "@api/types";

interface Props {
  labels: MemberLabels;
  actions: MemberListActions;
  usernames: string[];
  isLoading: boolean;
  update: UseMutationResult<void, Error, MembershipPatch>;
  /** Shown instead of the card when `actions.list` is false. */
  notAllowedMessage: string;
}

/**
 * A single member list with its add dialog and remove actions, shared by the
 * course owners and the LMS wide lists (LMS admins, course creators). The
 * caller owns the list query and update mutation, so it decides which endpoint
 * is used and whether the list is fetched at all.
 */
export function MemberListCard({
  labels,
  actions,
  usernames,
  isLoading,
  update,
  notAllowedMessage,
}: Props) {
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const selection = useSelection();

  const addText = memberListActionText.add(labels);

  if (!actions.list) {
    return <p className="text-gray-500">{notAllowedMessage}</p>;
  }

  return (
    <div className="max-w-2xl">
      <AddMembersDialog
        open={addDialogOpen}
        roleLabel={labels.singular}
        onCancel={() => setAddDialogOpen(false)}
        onConfirm={(names) => {
          update.mutate({ add: names });
          setAddDialogOpen(false);
        }}
      />
      <Card>
        {update.error && (
          <Alert
            className="mb-4"
            title={`Could not update the ${labels.plural.toLowerCase()}`}
          >
            {getErrorMessage(update.error)}
          </Alert>
        )}
        <div className="flex items-center justify-between mb-4">
          <CardTitle>{labels.plural}</CardTitle>
          {actions.add && (
            <Button
              variant="primary"
              onClick={() => setAddDialogOpen(true)}
              disabled={update.isPending}
              className="px-3 py-2 text-xs"
              title={addText.description}
            >
              + {addText.label}
            </Button>
          )}
        </div>
        <MemberDataTableWithCurrentUser
          rows={usernames}
          isLoading={isLoading}
          selected={selection.selected}
          onSelect={selection.toggle}
          onSelectAll={selection.toggleRows}
          onRemove={(username) =>
            update.mutate(
              { remove: [username] },
              { onSuccess: () => selection.remove(username) },
            )
          }
          onRemoveSelected={() => {
            if (selection.selected.size === 0) return;
            update.mutate(
              { remove: Array.from(selection.selected) },
              { onSuccess: selection.clear },
            );
          }}
          canRemove={actions.remove}
          removeLabel={labels.singular}
          isMutating={update.isPending}
        />
      </Card>
    </div>
  );
}
