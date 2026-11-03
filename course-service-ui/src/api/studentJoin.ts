import { requests } from "./client";
import { urlJoin } from "./http";
import { config } from "@config";
import type { StudentJoinInfo } from "./types";

const student_join_url = urlJoin(config.apiUrl, "student-join");

export const studentJoinAPI = {
  fetchInfo: async (token: string): Promise<StudentJoinInfo> => {
    return requests.get<StudentJoinInfo>(urlJoin(student_join_url, token));
  },
  join: async (token: string): Promise<void> => {
    return requests.post<void>(urlJoin(student_join_url, token), {});
  },
};
