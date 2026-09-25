import { useState } from "react";
import { Button } from "@components/ui/Button";
import { Modal } from "@components/ui/Modal";
import { RoleInfoLink } from "@components/actions/RoleInfoLink";
import type { MembershipRole } from "@domain/roles";

interface AddMembersDialogProps {
  open: boolean;
  roleLabel: string;
  /** Offers to explain what the role can do before anyone is added to it. */
  role?: MembershipRole;
  onCancel: () => void;
  onConfirm: (usernames: string[]) => void;
}

const parseUsernames = (rawInput: string): string[] =>
  Array.from(
    new Set(
      rawInput
        .split(/[\n,;\s]+/)
        .map((v) => v.trim())
        .filter((v) => v.length > 0),
    ),
  );

export function AddMembersDialog({
  open,
  roleLabel,
  role,
  onCancel,
  onConfirm,
}: AddMembersDialogProps) {
  const [input, setInput] = useState("");
  const [error, setError] = useState("");

  const handleConfirm = () => {
    const usernames = parseUsernames(input);
    if (usernames.length === 0) {
      setError("Please enter at least one username.");
      return;
    }
    onConfirm(usernames);
    setInput("");
    setError("");
  };

  const handleCancel = () => {
    setInput("");
    setError("");
    onCancel();
  };

  return (
    <Modal
      open={open}
      onClose={handleCancel}
      title={`Add ${roleLabel}`}
      description="Enter one username per line. Commas and spaces are also accepted."
      footer={
        <>
          <Button variant="secondary" onClick={handleCancel}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleConfirm}>
            Add {roleLabel}
          </Button>
        </>
      }
    >
      <textarea
        value={input}
        onChange={(e) => {
          setInput(e.target.value);
          if (error) setError("");
        }}
        placeholder={"alice\nbob\ncharlie"}
        rows={8}
        autoFocus
        className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-hbrs-dark-blue focus:outline-none resize-none font-mono"
      />
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
      {role && (
        <div className="mt-3">
          <RoleInfoLink role={role} />
        </div>
      )}
    </Modal>
  );
}
