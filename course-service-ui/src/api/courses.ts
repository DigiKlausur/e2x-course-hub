import { requests } from "./client";
import { urlJoin } from "./http";
import { config } from "../config";
import type { CourseDetails, CoursesResponse } from "../types";

const base_url = config.apiUrl;
const courses_url = urlJoin(base_url, "courses");

export const courseAPI = {
  fetchCourses: async (
    params: Record<string, string> | undefined = undefined,
  ): Promise<CoursesResponse> => {
    return requests.get(courses_url, params) as Promise<CoursesResponse>;
  },
  fetchCourseDetails: async (
    courseId: string,
    termId: string,
  ): Promise<CourseDetails> => {
    const url = urlJoin(courses_url, courseId, termId);
    return requests.get(url) as Promise<CourseDetails>;
  },
  fetchPermissionsInCourse: async (
    courseId: string,
    termId: string,
  ): Promise<unknown> => {
    return requests.get(urlJoin(base_url, "permissions", courseId, termId));
  },
  fetchAssignableRoles: async (
    courseId: string,
    termId: string,
  ): Promise<{ roles: string[] }> => {
    const url = urlJoin(base_url, "roles", "assignable", courseId, termId);
    return requests.get(url) as Promise<{ roles: string[] }>;
  },
};
