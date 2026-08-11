import { requests } from "./client";
import { urlJoin } from "./http";
import { config } from "../config";
import type { MembershipPatch, MembershipCollectionResponse } from "./types";

const base_url = config.apiUrl;
const hub_url = urlJoin(base_url, "hub");
const courses_url = urlJoin(base_url, "courses");

const course_url = (courseId: string) => urlJoin(courses_url, courseId);
const term_url = (courseId: string, termId: string) =>
  urlJoin(course_url(courseId), "terms", termId);

export const membershipAPI = {
  hub: {
    fetchHubAdmins: async (): Promise<MembershipCollectionResponse> => {
      return requests.get(
        urlJoin(hub_url, "admins"),
      ) as Promise<MembershipCollectionResponse>;
    },
    updateHubAdmins: async (patch: MembershipPatch): Promise<void> => {
      return requests.patch(urlJoin(hub_url, "admins"), patch) as Promise<void>;
    },
    fetchCourseCreators: async (): Promise<MembershipCollectionResponse> => {
      return requests.get(
        urlJoin(hub_url, "course-creators"),
      ) as Promise<MembershipCollectionResponse>;
    },
    updateCourseCreators: async (patch: MembershipPatch): Promise<void> => {
      return requests.patch(
        urlJoin(hub_url, "course-creators"),
        patch,
      ) as Promise<void>;
    },
  },
  course: {
    fetchOwners: async (
      courseId: string,
    ): Promise<MembershipCollectionResponse> => {
      return requests.get(
        urlJoin(course_url(courseId), "owners"),
      ) as Promise<MembershipCollectionResponse>;
    },
    updateOwners: async (
      courseId: string,
      patch: MembershipPatch,
    ): Promise<void> => {
      return requests.patch(
        urlJoin(course_url(courseId), "owners"),
        patch,
      ) as Promise<void>;
    },
  },
  term: {
    fetchInstructors: async (
      courseId: string,
      termId: string,
    ): Promise<MembershipCollectionResponse> => {
      return requests.get(
        urlJoin(term_url(courseId, termId), "instructors"),
      ) as Promise<MembershipCollectionResponse>;
    },
    updateInstructors: async (
      courseId: string,
      termId: string,
      patch: MembershipPatch,
    ): Promise<void> => {
      return requests.patch(
        urlJoin(term_url(courseId, termId), "instructors"),
        patch,
      ) as Promise<void>;
    },
    fetchTeachingAssistants: async (
      courseId: string,
      termId: string,
    ): Promise<MembershipCollectionResponse> => {
      return requests.get(
        urlJoin(term_url(courseId, termId), "teaching-assistants"),
      ) as Promise<MembershipCollectionResponse>;
    },
    updateTeachingAssistants: async (
      courseId: string,
      termId: string,
      patch: MembershipPatch,
    ): Promise<void> => {
      return requests.patch(
        urlJoin(term_url(courseId, termId), "teaching-assistants"),
        patch,
      ) as Promise<void>;
    },
    fetchStudents: async (
      courseId: string,
      termId: string,
    ): Promise<MembershipCollectionResponse> => {
      return requests.get(
        urlJoin(term_url(courseId, termId), "students"),
      ) as Promise<MembershipCollectionResponse>;
    },
    updateStudents: async (
      courseId: string,
      termId: string,
      patch: MembershipPatch,
    ): Promise<void> => {
      return requests.patch(
        urlJoin(term_url(courseId, termId), "students"),
        patch,
      ) as Promise<void>;
    },
    fetchObservers: async (
      courseId: string,
      termId: string,
    ): Promise<MembershipCollectionResponse> => {
      return requests.get(
        urlJoin(term_url(courseId, termId), "observers"),
      ) as Promise<MembershipCollectionResponse>;
    },
    updateObservers: async (
      courseId: string,
      termId: string,
      patch: MembershipPatch,
    ): Promise<void> => {
      return requests.patch(
        urlJoin(term_url(courseId, termId), "observers"),
        patch,
      ) as Promise<void>;
    },
  },
};
