import { useState } from "react";
import { courseMemberAPI } from "@/api";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

interface AddUsersToCourseDialogProps {
  courseId: string;
  termId: string;
  role: string;
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const AddUsersToCourseDialog = ({
  courseId,
  termId,
  role,
  open,
  onClose,
  onSuccess,
}: AddUsersToCourseDialogProps) => {
  const [usernames, setUsernames] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const rolePluralName = `${role.toLowerCase()}s`;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!usernames.trim()) {
      setError("Please enter at least one username");
      return;
    }

    // Parse usernames (one per line, filter empty lines)
    const usernameList = usernames
      .split("\n")
      .map((u) => u.trim())
      .filter((u) => u.length > 0);

    if (usernameList.length === 0) {
      setError("Please enter at least one valid username");
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      await courseMemberAPI.addCourseMembers(
        courseId,
        termId,
        role,
        usernameList,
      );
      onSuccess(); // Refresh the members table
      onClose(); // Close the modal
    } catch (err) {
      console.error("Error adding members:", err);
      setError(err instanceof Error ? err.message : "Failed to add members");
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>
            Add{" "}
            {rolePluralName.charAt(0).toUpperCase() + rolePluralName.slice(1)}{" "}
            to Course
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 bg-destructive/10 border border-destructive/20 rounded text-destructive text-sm">
              {error}
            </div>
          )}

          <div className="grid gap-2">
            <Label htmlFor="usernames-input">Usernames (one per line):</Label>
            <Textarea
              id="usernames-input"
              value={usernames}
              onChange={(e) => setUsernames(e.target.value)}
              placeholder={`Enter usernames to add as ${rolePluralName}, one per line\nExample:\n${role}1\n${role}2\n${role}3`}
              rows={10}
              disabled={submitting}
              required
            />
            <small className="block mt-1 text-xs text-muted-foreground">
              Enter one username per line. Empty lines will be ignored.
            </small>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={submitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={submitting}>
              {submitting
                ? "Adding..."
                : `Add ${rolePluralName.charAt(0).toUpperCase() + rolePluralName.slice(1)}`}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default AddUsersToCourseDialog;
