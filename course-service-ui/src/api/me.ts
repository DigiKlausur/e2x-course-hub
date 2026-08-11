import { requests } from "./client";
import { urlJoin } from "./http";
import { config } from "../config";
import type { CurrentUser } from "./types";

const base_url = config.apiUrl;

export const meAPI = {
  fetch: async (): Promise<CurrentUser> => {
    return requests.get(urlJoin(base_url, "me")) as Promise<CurrentUser>;
  },
};
