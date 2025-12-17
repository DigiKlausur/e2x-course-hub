import { requests } from "./client";
import { urlJoin } from "./http";
import { config } from "../config";
import type { Profile } from "../types";

const base_url = config.apiUrl;
const profiles_url = urlJoin(base_url, "profiles");

export const profileAPI = {
  fetchProfile: async (
    courseId: string,
    termId: string,
    profileId: string,
  ): Promise<Profile> => {
    const url = urlJoin(profiles_url, courseId, termId, profileId);
    return requests.get(url) as Promise<Profile>;
  },
};
