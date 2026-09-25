import { useState } from "react";
import { Info } from "lucide-react";
import { type MembershipRole, memberLabels } from "@domain/roles";
import { RoleActionsModal, type RoleContext } from "./RoleActionsModal";

interface Props {
  role: MembershipRole;
  /** The course and semester the link is shown in, named in the explanation. */
  context?: RoleContext;
}

/** "What can Teaching Assistants do?", opening the explanation of the role. */
export function RoleInfoLink({ role, context }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="inline-flex items-center gap-1 text-sm text-hbrs-dark-blue hover:underline"
      >
        <Info className="size-4" />
        What can {memberLabels[role].plural} do?
      </button>
      <RoleActionsModal
        role={role}
        open={open}
        onClose={() => setOpen(false)}
        context={context}
      />
    </>
  );
}
