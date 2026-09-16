import { requests } from "./client";
import { urlJoin } from "./http";
import { config } from "../config";
import type { MembershipPatch, MembershipCollectionResponse } from "./types";

const base_url = config.apiUrl;
const lms_url = urlJoin(base_url, "lms");
const courses_url = urlJoin(base_url, "courses");

const course_url = (courseId: string) => urlJoin(courses_url, courseId);
const term_url = (courseId: string, termId: string) =>
  urlJoin(course_url(courseId), "terms", termId);

// Every membership PATCH answers 204 with no body.
const fetchCollection = (url: string) =>
  requests.get<MembershipCollectionResponse>(url);
const patchCollection = (url: string, patch: MembershipPatch) =>
  requests.patch<void>(url, patch);

export const membershipAPI = {
  lms: {
    fetchLMSAdmins: async (): Promise<MembershipCollectionResponse> => {
      return fetchCollection(urlJoin(lms_url, "admins"));
    },
    updateLMSAdmins: async (patch: MembershipPatch): Promise<void> => {
      return patchCollection(urlJoin(lms_url, "admins"), patch);
    },
    fetchCourseCreators: async (): Promise<MembershipCollectionResponse> => {
      return fetchCollection(urlJoin(lms_url, "course-creators"));
    },
    updateCourseCreators: async (patch: MembershipPatch): Promise<void> => {
      return patchCollection(urlJoin(lms_url, "course-creators"), patch);
    },
  },
  course: {
    fetchOwners: async (
      courseId: string,
    ): Promise<MembershipCollectionResponse> => {
      return fetchCollection(urlJoin(course_url(courseId), "owners"));
    },
    updateOwners: async (
      courseId: string,
      patch: MembershipPatch,
    ): Promise<void> => {
      return patchCollection(urlJoin(course_url(courseId), "owners"), patch);
    },
  },
  term: {
    fetchInstructors: async (
      courseId: string,
      termId: string,
    ): Promise<MembershipCollectionResponse> => {
      return fetchCollection(
        urlJoin(term_url(courseId, termId), "instructors"),
      );
    },
    updateInstructors: async (
      courseId: string,
      termId: string,
      patch: MembershipPatch,
    ): Promise<void> => {
      return patchCollection(
        urlJoin(term_url(courseId, termId), "instructors"),
        patch,
      );
    },
    fetchTeachingAssistants: async (
      courseId: string,
      termId: string,
    ): Promise<MembershipCollectionResponse> => {
      return fetchCollection(
        urlJoin(term_url(courseId, termId), "teaching-assistants"),
      );
    },
    updateTeachingAssistants: async (
      courseId: string,
      termId: string,
      patch: MembershipPatch,
    ): Promise<void> => {
      return patchCollection(
        urlJoin(term_url(courseId, termId), "teaching-assistants"),
        patch,
      );
    },
    fetchStudents: async (
      courseId: string,
      termId: string,
    ): Promise<MembershipCollectionResponse> => {
      return fetchCollection(urlJoin(term_url(courseId, termId), "students"));
    },
    updateStudents: async (
      courseId: string,
      termId: string,
      patch: MembershipPatch,
    ): Promise<void> => {
      return patchCollection(
        urlJoin(term_url(courseId, termId), "students"),
        patch,
      );
    },
    fetchObservers: async (
      courseId: string,
      termId: string,
    ): Promise<MembershipCollectionResponse> => {
      return fetchCollection(urlJoin(term_url(courseId, termId), "observers"));
    },
    updateObservers: async (
      courseId: string,
      termId: string,
      patch: MembershipPatch,
    ): Promise<void> => {
      return patchCollection(
        urlJoin(term_url(courseId, termId), "observers"),
        patch,
      );
    },
  },
};
