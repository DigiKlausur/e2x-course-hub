import { requests } from "./client";
import { urlJoin } from "./http";
import { config } from "../config";

const base_url = config.apiUrl;
const course_members_url = urlJoin(base_url, "course-members");

export const courseMemberAPI = {
  fetchCourseMembers: async (
    courseId: string,
    termId: string,
  ): Promise<unknown> => {
    return requests.get(urlJoin(course_members_url, courseId, termId));
  },
  addCourseMembers: async (
    courseId: string,
    termId: string,
    roleId: string,
    members: string[],
  ): Promise<unknown> => {
    const url = urlJoin(course_members_url, courseId, termId);
    return requests.post(url, { role: roleId, usernames: members });
  },
  removeCourseMembers: async (
    courseId: string,
    termId: string,
    members: string[],
  ): Promise<unknown> => {
    const url = urlJoin(course_members_url, courseId, termId);
    return requests.del(url, { usernames: members });
  },
};
