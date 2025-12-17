import { useState, useCallback } from "react";
import { courseMemberAPI } from "../api";
import { getConfig } from "../config";

interface UseMemberDeleteOptions {
  courseId: string;
  termId: string;
  onSuccess?: () => void;
}

export function useMemberDelete({
  courseId,
  termId,
  onSuccess,
}: UseMemberDeleteOptions) {
  const [deletingUser, setDeletingUser] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [confirmDialog, setConfirmDialog] = useState<{
    username: string;
    isCurrentUser: boolean;
  } | null>(null);

  const initiateDelete = useCallback(
    (username: string) => {
      const config = getConfig();
      const isCurrentUser = username === config.user.name;
      setConfirmDialog({ username, isCurrentUser });
    },
    [],
  );

  const confirmDelete = useCallback(
    async (usernameInput?: string) => {
      if (!confirmDialog) return;

      const { username, isCurrentUser } = confirmDialog;

      // For current user, validate username input
      if (isCurrentUser && usernameInput !== username) {
        return; // Validation failed, dialog will show error
      }

      setConfirmDialog(null);

      try {
        setDeletingUser(username);
        setDeleteError(null);
        await courseMemberAPI.removeCourseMembers(courseId, termId, [username]);
        onSuccess?.();
      } catch (err) {
        console.error("Error deleting user:", err);
        setDeleteError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setDeletingUser(null);
      }
    },
    [confirmDialog, courseId, termId, onSuccess],
  );

  const cancelDelete = useCallback(() => {
    setConfirmDialog(null);
  }, []);

  const clearError = useCallback(() => {
    setDeleteError(null);
  }, []);

  return {
    deletingUser,
    deleteError,
    confirmDialog,
    initiateDelete,
    confirmDelete,
    cancelDelete,
    clearError,
  };
}
