import { requests } from "./client";
import { urlJoin } from "./http";
import { config } from "../config";
import type {
  CourseCollectionResponse,
  CourseDetailResponse,
  CourseMetadata,
  CourseMetadataUpdate,
  CourseConfig,
  TermSummaryResponse,
  TermDetailResponse,
  Environment,
  EnvironmentUpdate,
  CreateTermRequest,
} from "./types";

const base_url = config.apiUrl;
const courses_url = urlJoin(base_url, "courses");

export const courseAPI = {
  fetchCourses: async (): Promise<CourseCollectionResponse> => {
    return requests.get(courses_url) as Promise<CourseCollectionResponse>;
  },
  fetchCourse: async (courseId: string): Promise<CourseDetailResponse> => {
    return requests.get(
      urlJoin(courses_url, courseId),
    ) as Promise<CourseDetailResponse>;
  },
  createCourse: async (courseConfig: CourseConfig): Promise<CourseMetadata> => {
    return requests.post(courses_url, courseConfig) as Promise<CourseMetadata>;
  },
  deleteCourse: async (courseId: string): Promise<void> => {
    return requests.delete(urlJoin(courses_url, courseId)) as Promise<void>;
  },
  fetchCourseMetadata: async (courseId: string): Promise<CourseMetadata> => {
    return requests.get(
      urlJoin(courses_url, courseId, "metadata"),
    ) as Promise<CourseMetadata>;
  },
  updateCourseMetadata: async (
    courseId: string,
    updateData: CourseMetadataUpdate,
  ): Promise<CourseMetadata> => {
    return requests.patch(
      urlJoin(courses_url, courseId, "metadata"),
      updateData,
    ) as Promise<CourseMetadata>;
  },
  fetchCourseEnvironment: async (courseId: string): Promise<Environment> => {
    return requests.get(
      urlJoin(courses_url, courseId, "environment"),
    ) as Promise<Environment>;
  },
  updateCourseEnvironment: async (
    courseId: string,
    updateData: EnvironmentUpdate,
  ): Promise<Environment> => {
    return requests.patch(
      urlJoin(courses_url, courseId, "environment"),
      updateData,
    ) as Promise<Environment>;
  },
  fetchTerms: async (courseId: string): Promise<TermSummaryResponse[]> => {
    return requests.get(urlJoin(courses_url, courseId, "terms")) as Promise<
      TermSummaryResponse[]
    >;
  },
  fetchTerm: async (
    courseId: string,
    termId: string,
  ): Promise<TermDetailResponse> => {
    return requests.get(
      urlJoin(courses_url, courseId, "terms", termId),
    ) as Promise<TermDetailResponse>;
  },
  fetchTermEnvironment: async (
    courseId: string,
    termId: string,
  ): Promise<Environment> => {
    return requests.get(
      urlJoin(courses_url, courseId, "terms", termId, "environment"),
    ) as Promise<Environment>;
  },
  updateTermEnvironment: async (
    courseId: string,
    termId: string,
    updateData: EnvironmentUpdate,
  ): Promise<Environment> => {
    return requests.patch(
      urlJoin(courses_url, courseId, "terms", termId, "environment"),
      updateData,
    ) as Promise<Environment>;
  },
  createTerm: async (
    courseId: string,
    termId: string,
    termConfig?: CreateTermRequest,
  ): Promise<TermSummaryResponse> => {
    return requests.post(
      urlJoin(courses_url, courseId, "terms", termId),
      termConfig || {},
    ) as Promise<TermSummaryResponse>;
  },
  deleteTerm: async (courseId: string, termId: string): Promise<void> => {
    return requests.delete(
      urlJoin(courses_url, courseId, "terms", termId),
    ) as Promise<void>;
  },
};
