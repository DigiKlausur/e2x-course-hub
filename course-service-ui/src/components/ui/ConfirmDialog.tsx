import { useState } from "react";
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
}: ConfirmDialogProps) {
  const [inputValue, setInputValue] = useState("");

  if (!open) return null;

  const canConfirm =
    !requireConfirmationText || inputValue === requireConfirmationText;

  const handleConfirm = () => {
    if (!canConfirm) return;

    onConfirm();
    setInputValue("");
  };

  const handleClose = () => {
    setInputValue("");
    onClose();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      onClick={(e) => {
        if (e.target === e.currentTarget) handleClose();
      }}
    >
      <div className="w-full max-w-md rounded-2xl bg-white shadow-2xl ring-1 ring-black/5 animate-in fade-in zoom-in-95">
        <div className="px-6 pt-6">
          <h2 className="text-lg font-semibold text-gray-900">
            {title}
          </h2>

          <p className="mt-2 text-sm leading-6 text-gray-600">
            {message}
          </p>

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
        </div>

        <div className="mt-6 flex justify-end gap-3 rounded-b-2xl bg-gray-50 px-6 py-4">
          <Button
            variant="secondary"
            onClick={handleClose}
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
        </div>
      </div>
    </div>
  );
}