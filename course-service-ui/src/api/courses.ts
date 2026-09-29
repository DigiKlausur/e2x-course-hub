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
    return requests.get<CourseCollectionResponse>(courses_url);
  },
  fetchCourse: async (courseId: string): Promise<CourseDetailResponse> => {
    return requests.get<CourseDetailResponse>(urlJoin(courses_url, courseId));
  },
  createCourse: async (courseConfig: CourseConfig): Promise<CourseMetadata> => {
    return requests.post<CourseMetadata>(courses_url, courseConfig);
  },
  deleteCourse: async (courseId: string): Promise<void> => {
    return requests.delete(urlJoin(courses_url, courseId));
  },
  fetchCourseMetadata: async (courseId: string): Promise<CourseMetadata> => {
    return requests.get<CourseMetadata>(
      urlJoin(courses_url, courseId, "metadata"),
    );
  },
  updateCourseMetadata: async (
    courseId: string,
    updateData: CourseMetadataUpdate,
  ): Promise<CourseMetadata> => {
    return requests.patch<CourseMetadata>(
      urlJoin(courses_url, courseId, "metadata"),
      updateData,
    );
  },
  fetchCourseEnvironment: async (courseId: string): Promise<Environment> => {
    return requests.get<Environment>(
      urlJoin(courses_url, courseId, "environment"),
    );
  },
  updateCourseEnvironment: async (
    courseId: string,
    updateData: EnvironmentUpdate,
  ): Promise<Environment> => {
    return requests.patch<Environment>(
      urlJoin(courses_url, courseId, "environment"),
      updateData,
    );
  },
  fetchTerms: async (courseId: string): Promise<TermSummaryResponse[]> => {
    return requests.get<TermSummaryResponse[]>(
      urlJoin(courses_url, courseId, "terms"),
    );
  },
  fetchTerm: async (
    courseId: string,
    termId: string,
  ): Promise<TermDetailResponse> => {
    return requests.get<TermDetailResponse>(
      urlJoin(courses_url, courseId, "terms", termId),
    );
  },
  fetchTermEnvironment: async (
    courseId: string,
    termId: string,
  ): Promise<Environment> => {
    return requests.get<Environment>(
      urlJoin(courses_url, courseId, "terms", termId, "environment"),
    );
  },
  updateTermEnvironment: async (
    courseId: string,
    termId: string,
    updateData: EnvironmentUpdate,
  ): Promise<Environment> => {
    return requests.patch<Environment>(
      urlJoin(courses_url, courseId, "terms", termId, "environment"),
      updateData,
    );
  },
  createTerm: async (
    courseId: string,
    termId: string,
    termConfig?: CreateTermRequest,
  ): Promise<TermDetailResponse> => {
    return requests.post<TermDetailResponse>(
      urlJoin(courses_url, courseId, "terms", termId),
      termConfig ?? {},
    );
  },
  deleteTerm: async (courseId: string, termId: string): Promise<void> => {
    return requests.delete(urlJoin(courses_url, courseId, "terms", termId));
  },
};
