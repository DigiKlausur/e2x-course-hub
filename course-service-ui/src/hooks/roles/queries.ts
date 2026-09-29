import { useQuery } from "@tanstack/react-query";
import { rolesAPI } from "@api";
import type { RoleActionsResponse, RoleName } from "@api/types";

/**
 * What a role can and cannot do. The same for every course and semester and
 * only changes with a deployment, so it is fetched once per role.
 */
export function useRoleActions(role: RoleName, enabled = true) {
  return useQuery<RoleActionsResponse>({
    queryKey: ["roles", role, "actions"],
    queryFn: () => rolesAPI.fetchActions(role),
    enabled,
    staleTime: Infinity,
  });
}
