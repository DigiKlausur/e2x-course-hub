import { useMutation } from "@tanstack/react-query";
import { studentJoinAPI } from "@api";

/**
 * Joins the current user as a student. The join info is deliberately not
 * invalidated: the server reads the user's groups from a cached hub user model,
 * so a refetch would still report "can join" for a few minutes. The join page
 * tracks that the user has joined itself.
 */
export function useJoinAsStudent(token: string) {
  return useMutation({
    mutationFn: () => studentJoinAPI.join(token),
  });
}
