import { useQuery } from "@tanstack/react-query";
import { meAPI } from "@api";
import type { CurrentUser } from "@api/types";

export function useCurrentUser() {
  return useQuery<CurrentUser>({
    queryKey: ["me"],
    queryFn: () => meAPI.fetch(),
  });
}
