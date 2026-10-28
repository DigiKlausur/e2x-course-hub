import { useState } from "react";
import { Modal } from "./Modal";
import { Button } from "./Button";

export interface ConfirmDialogProps {
  open: boolean;
  onClose: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  variant?: "default" | "destructive";
  requireConfirmationText?: string;
  /** Set while the confirmed action is in flight, to block a second submit. */
  isConfirming?: boolean;
}

export function ConfirmDialog({
  open,
  onClose,
  title,
  message,
  confirmText = "Confirm",
  cancelText = "Cancel",
  onConfirm,
  variant = "default",
  requireConfirmationText,
  isConfirming = false,
}: ConfirmDialogProps) {
  const [inputValue, setInputValue] = useState("");

  const canConfirm =
    (!requireConfirmationText || inputValue === requireConfirmationText) &&
    !isConfirming;

  const handleConfirm = () => {
    if (!canConfirm) return;

    onConfirm();
    setInputValue("");
  };

  const handleClose = () => {
    // Don't let the close button dismiss the dialog mid-request; the caller
    // closes it once the action resolves.
    if (isConfirming) return;
    setInputValue("");
    onClose();
  };

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title={title}
      footer={
        <>
          <Button
            variant="secondary"
            onClick={handleClose}
            disabled={isConfirming}
          >
            {cancelText}
          </Button>

          <Button
            variant={variant === "destructive" ? "danger" : "primary"}
            onClick={handleConfirm}
            disabled={!canConfirm}
          >
            {confirmText}
          </Button>
        </>
      }
    >
      <p className="text-sm leading-6 text-gray-600">{message}</p>

      {requireConfirmationText && (
        <div className="mt-5">
          <label
            htmlFor="confirmation-input"
            className="block text-sm font-medium text-gray-700"
          >
            Type{" "}
            <span className="font-semibold text-gray-900">
              {requireConfirmationText}
            </span>{" "}
            to confirm
          </label>

          <input
            id="confirmation-input"
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isConfirming}
            className="
              mt-2 block w-full rounded-lg border border-gray-300
              px-3 py-2 text-sm text-gray-900
              shadow-sm outline-none
              transition
              focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20
            "
            autoFocus
          />
        </div>
      )}
    </Modal>
  );
}
