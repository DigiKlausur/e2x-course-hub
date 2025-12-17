import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface PromptDialogProps {
  title: string;
  message: string;
  placeholder?: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: (value: string) => void;
  onCancel: () => void;
  validateInput?: (value: string) => boolean;
  validationMessage?: string;
}

const PromptDialog = ({
  title,
  message,
  placeholder = "",
  confirmText = "Confirm",
  cancelText = "Cancel",
  onConfirm,
  onCancel,
  validateInput,
  validationMessage = "Invalid input",
}: PromptDialogProps) => {
  const [inputValue, setInputValue] = useState("");
  const [error, setError] = useState("");

  const handleConfirm = () => {
    if (validateInput && !validateInput(inputValue)) {
      setError(validationMessage);
      return;
    }
    onConfirm(inputValue);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
    if (error) setError("");
  };

  return (
    <Dialog open={true} onOpenChange={(open) => !open && onCancel()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription className="whitespace-pre-line">
            {message}
          </DialogDescription>
        </DialogHeader>

        <Input
          value={inputValue}
          onChange={handleInputChange}
          placeholder={placeholder}
          autoFocus
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleConfirm();
            } else if (e.key === "Escape") {
              onCancel();
            }
          }}
        />

        {error && <p className="text-sm text-destructive">{error}</p>}

        <DialogFooter>
          <Button onClick={onCancel} variant="outline">
            {cancelText}
          </Button>
          <Button onClick={handleConfirm} variant="destructive">
            {confirmText}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export { PromptDialog };
export type { PromptDialogProps };
