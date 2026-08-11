import { useQuery, queryOptions } from "@tanstack/react-query";
import { courseAPI } from "@api";
import { courseKeys } from "./keys";

const courseQuery = (courseId: string) =>
  queryOptions({
    queryKey: courseKeys.detail(courseId),
    queryFn: () => courseAPI.fetchCourse(courseId),
    enabled: !!courseId,
  });

const coursesQuery = () =>
  queryOptions({
    queryKey: courseKeys.all,
    queryFn: () => courseAPI.fetchCourses(),
  });

const termQuery = (courseId: string, termId: string) =>
  queryOptions({
    queryKey: courseKeys.terms.detail(courseId, termId),
    queryFn: () => courseAPI.fetchTerm(courseId, termId),
    enabled: !!courseId && !!termId,
  });

const termsQuery = (courseId: string) =>
  queryOptions({
    queryKey: courseKeys.terms.all(courseId),
    queryFn: () => courseAPI.fetchTerms(courseId),
    enabled: !!courseId,
  });

export function useCourses() {
  return useQuery(coursesQuery());
}

export function useCourse(courseId: string) {
  return useQuery(courseQuery(courseId));
}

export function useCourseMetadata(courseId: string) {
  return useQuery({
    ...courseQuery(courseId),
    select: (course) => course.metadata,
  });
}

export function useCourseEnvironment(courseId: string) {
  return useQuery({
    ...courseQuery(courseId),
    select: (course) => course.environment,
  });
}

export function useTerms(courseId: string) {
  return useQuery(termsQuery(courseId));
}

export function useTerm(courseId: string, termId: string) {
  return useQuery(termQuery(courseId, termId));
}

export function useTermEnvironment(courseId: string, termId: string) {
  return useQuery({
    ...termQuery(courseId, termId),
    select: (term) => term.environment,
  });
}
