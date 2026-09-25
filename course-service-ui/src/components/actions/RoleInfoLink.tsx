import { useState } from "react";
import { Info } from "lucide-react";
import { type MembershipRole, memberLabels } from "@domain/roles";
import { RoleActionsModal } from "./RoleActionsModal";

interface Props {
  role: MembershipRole;
}

/** "What can Teaching Assistants do?", opening the explanation of the role. */
export function RoleInfoLink({ role }: Props) {
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
      />
    </>
  );
}
