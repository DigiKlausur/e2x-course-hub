import { useState } from "react";
import { Button } from "@components/ui/Button";
import { Modal } from "@components/ui/Modal";
import type { ActionTextMap } from "@domain/actions";
import { ActionList } from "./ActionList";

interface Props<T> {
  actions: T;
  texts: ActionTextMap<T>;
  /** Where the actions apply, e.g. "in this semester". */
  scope: string;
}

/** Shows what the current user can do on this page, e.g. which environments they can start. */
export function YourAccessButton<T extends object>({
  actions,
  texts,
  scope,
}: Props<T>) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button
        variant="secondary"
        onClick={() => setOpen(true)}
        className="px-3 py-2 text-xs"
      >
        Your access
      </Button>
      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title="Your access"
        description={`What you can do ${scope}.`}
        footer={
          <Button variant="secondary" onClick={() => setOpen(false)}>
            Close
          </Button>
        }
      >
        <ActionList actions={actions} texts={texts} />
      </Modal>
    </>
  );
}
