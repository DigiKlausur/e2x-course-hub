import {
  useQueryClient,
  useMutation,
  QueryClient,
} from "@tanstack/react-query";
import { courseAPI } from "@api";
import type {
  CourseMetadataUpdate,
  CourseConfig,
  EnvironmentUpdate,
  CreateTermRequest,
} from "@api/types";

import { courseKeys } from "./keys";

const invalidateCourse = (queryClient: QueryClient, courseId: string) =>
  queryClient.invalidateQueries({
    queryKey: courseKeys.detail(courseId),
  });

const invalidateCourses = (queryClient: QueryClient) =>
  queryClient.invalidateQueries({
    queryKey: courseKeys.all,
  });

const invalidateTerms = (queryClient: QueryClient, courseId: string) =>
  queryClient.invalidateQueries({
    queryKey: courseKeys.terms.all(courseId),
  });

const invalidateTerm = (
  queryClient: QueryClient,
  courseId: string,
  termId: string,
) =>
  queryClient.invalidateQueries({
    queryKey: courseKeys.terms.detail(courseId, termId),
  });

export function useCreateCourse() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (courseConfig: CourseConfig) =>
      courseAPI.createCourse(courseConfig),
    onSuccess: () => invalidateCourses(queryClient),
  });
}

export function useDeleteCourse(courseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => courseAPI.deleteCourse(courseId),
    onSuccess: () =>
      Promise.all([
        invalidateCourse(queryClient, courseId),
        invalidateCourses(queryClient),
      ]),
  });
}
export function useUpdateCourseMetadata(courseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (updateData: CourseMetadataUpdate) =>
      courseAPI.updateCourseMetadata(courseId, updateData),
    onSuccess: () =>
      Promise.all([
        invalidateCourse(queryClient, courseId),
        invalidateCourses(queryClient),
      ]),
  });
}
export function useUpdateCourseEnvironment(courseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (updateData: EnvironmentUpdate) =>
      courseAPI.updateCourseEnvironment(courseId, updateData),
    onSuccess: () => invalidateCourse(queryClient, courseId),
  });
}

export function useCreateTerm(courseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      termId,
      termConfig,
    }: {
      termId: string;
      termConfig: CreateTermRequest;
    }) => courseAPI.createTerm(courseId, termId, termConfig),
    onSuccess: () => invalidateTerms(queryClient, courseId),
  });
}

export function useDeleteTerm(courseId: string, termId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => courseAPI.deleteTerm(courseId, termId),
    onSuccess: () =>
      Promise.all([
        invalidateCourse(queryClient, courseId),
        invalidateTerms(queryClient, courseId),
        invalidateTerm(queryClient, courseId, termId),
      ]),
  });
}

export function useUpdateTermEnvironment(courseId: string, termId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (updateData: EnvironmentUpdate) =>
      courseAPI.updateTermEnvironment(courseId, termId, updateData),
    onSuccess: () => invalidateTerm(queryClient, courseId, termId),
  });
}
