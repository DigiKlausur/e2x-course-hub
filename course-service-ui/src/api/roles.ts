import { requests } from "./client";
import { urlJoin } from "./http";
import { config } from "../config";
import type { RoleActionsResponse, RoleName } from "./types";

const roles_url = urlJoin(config.apiUrl, "roles");

export const rolesAPI = {
  fetchActions: async (role: RoleName): Promise<RoleActionsResponse> => {
    return requests.get<RoleActionsResponse>(
      urlJoin(roles_url, role, "actions"),
    );
  },
};
